import requests
import logging
import os
from datetime import datetime

class FigmaClient:
    def __init__(self, api_token):
        self.api_token = api_token
        self.base_url = "https://api.figma.com/v1"
        self.logger = logging.getLogger(__name__)

    def get_file(self, file_key):
        self.logger.info(f"Fetching file data for key: {file_key}")
        headers ={
            "X-Figma-Token": self.api_token
        }
        try:
            response = requests.get(f"{self.base_url}/files/{file_key}", headers=headers)
            response.raise_for_status()
            self.logger.info(f"Successfully retrieved file data. Response size: {len(response.content)} bytes")
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to fetch file data: {str(e)}")
            raise

    def get_images(self, file_key):
        self.logger.info(f"Starting image extraction for file: {file_key}")
        file_data = self.get_file(file_key)
        image_refs = []
        exportable_nodes = []
        document = file_data.get('document', {})
        children = document.get('children', [])
        self.logger.info(f"Found {len(children)} top-level nodes to process")

        for i, node in enumerate(children):
            self.logger.debug(f"Processing node {i+1}/{len(children)}: {node.get('name', 'Unnamed')}")
            node_images = self._extract_images(node)
            image_refs.extend(node_images)
            node_exportable = self._extract_exportable_nodes(node)
            exportable_nodes.extend(node_exportable)
        
        self.logger.info(f"Found {len(image_refs)} image references")
        self.logger.info(f"Found {len(exportable_nodes)} exportable nodes")

        urls = []

        if image_refs:
            bitmap_urls = self.get_image_urls(file_key, image_refs)
            urls.extend(bitmap_urls)
        
        if exportable_nodes:
            vector_urls = self.export_nodes_as_images(file_key, exportable_nodes)
            urls.extend(vector_urls)

        if not urls:
            self.logger.warning("No image URLs found in the Figma file.")
        
        return urls

    
    def get_image_urls(self, file_key, image_refs):
        self.logger.info(f"Converting {len(image_refs)} image references to URLs")
        headers = {
            "X-Figma-Token": self.api_token
        }

        # Filter out image references that don't contain ':' or '-' separators
        # These are typically invalid image reference hashes that cause 400 errors
        filtered_refs = []
        for ref in image_refs:
            if ref and isinstance(ref, str) and (':' in ref or '-' in ref):
                filtered_refs.append(ref)
            else:
                self.logger.warning(f"Filtering out image reference without separators: {ref}")
        
        self.logger.info(f"Filtered {len(image_refs)} -> {len(filtered_refs)} image references (removed {len(image_refs) - len(filtered_refs)} without separators)")

        unique_refs = list(set(filtered_refs))
        self.logger.info(f"Removed duplicates, processing {len(unique_refs)} unique images")

        if not unique_refs:
            self.logger.warning("No valid image references found after filtering")
            return []

        ids_param = ','.join(unique_refs)
        try:
            response = requests.get(
                f"{self.base_url}/images/{file_key}",
                headers=headers,
                params={"ids": ids_param, 'format': 'png'}
            )
            response.raise_for_status()
            data = response.json()
            images = data.get('images', {})
            urls = []
            for ref in unique_refs:
                if ref in images and images[ref]:
                    urls.append(images[ref])
                    self.logger.info(f"Successfully retrieved {len(urls)} image URLs")
                else:
                    self.logger.warning(f"No URL found for image reference: {ref}")
            
            self.logger.info(f"Total image URLs retrieved: {len(urls)}")
            return urls
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to retrieve image URLs: {str(e)}")
            raise

    def _extract_images(self, node):
        images = []
        node_name = node.get('name', 'Unnamed')
        node_type = node.get('type', 'Unknown')

        self._extract_images_from_fills(node, images, node_name)
        self._extract_images_from_effects(node, images, node_name)
        self._extract_images_from_strokes(node, images, node_name)

        if 'children' in node:
            self.logger.debug(f'Processing children of node {node_name} (type): {node_type}')
            for child in node['children']:
                images.extend(self._extract_images(child))
        return images

    def _extract_images_from_fills(self, node, images, node_name):
        fills = node.get('fills', [])
        for i, fill in enumerate(fills):
            if fill.get('type') == 'IMAGE' and 'imageRef' in fill:
                image_ref = fill['imageRef']
                images.append(image_ref)
                self.logger.info(f"Found image in fills of node {node_name}: {image_ref}")

    def _extract_images_from_effects(self, node, images, node_name):
        effects = node.get('effects', [])
        for effect in effects:
            if 'imageRef' in effect:
                image_ref = effect['imageRef']
                images.append(image_ref)
                self.logger.info(f"Found image in effects of node {node_name}: {image_ref}")
    
    def _extract_images_from_strokes(self, node, images, node_name):
        strokes = node.get('strokes', [])
        for stroke in strokes:
            if stroke.get('type') == 'IMAGE' and 'imageRef' in stroke:
                image_ref = stroke['imageRef']
                images.append(image_ref)
                self.logger.info(f"Found image in strokes of node {node_name}: {image_ref}")

    def _extract_exportable_nodes(self, node):
        exportable_nodes = []
        node_name = node.get('name', 'Unnamed')
        node_type = node.get('type', 'Unknown')
        node_id = node.get('id')

        exportable_types = ['COMPONENT', 'INSTANCE', 'FRAME', 'GROUP']
        if node_type in exportable_types:
            if node_type == 'COMPONENT' or (node_type in ['FRAME', 'GROUP'] and self._is_icon_sized(node)):
                exportable_nodes.append({
                    'id': node_id,
                    'name': node_name,
                    'type': node_type
                })
                self.logger.info(f"Node {node_name} (ID: {node_id}) is exportable")
        if 'children' in node:
            for child in node['children']:
                exportable_nodes.extend(self._extract_exportable_nodes(child))
        
        return exportable_nodes
    
    def _should_export_as_unit(self, node):
        node_type = node.get('type', 'Unknown')
        node_name = node.get('name', 'Unnamed')
        if node_type in ['COMPONENT', 'INSTANCE']:
            return True
        if node_type in ['FRAME', 'GROUP']:
            if self._is_icon_sized(node):
                return True
            if node.get('exportSettings'):
                self.logger.info(f"Node {node_name} (ID: {node.get('id')}) has export settings, exporting as unit")
                return True
            
            icon_keyworkds = ['icon', 'logo', 'symbol', 'badge', 'button', 'avatar']
            if any(keyword in node_name.lower() for keyword in icon_keyworkds):
                self.logger.info(f"Node {node_name} appears to be an icon/logo based on name, exporting as unit")
                return True
            
            if self._is_vector_composition(node):
                return True
        return False
    
    def _is_vector_composition(self, node):
        children = node.get('children', [])
        if not children:
            return False
        
        vector_types = ['VECTOR', 'BOOLEAN_OPERATION', 'STAR', 'POLYGON', 'ELIPSE', 'RECTANGLE']
        vector_count = 0
        tolta_count = len(children)

        for child in children:
            if child.get('type') in vector_types:
                vector_count += 1
        vector_ratio = vector_count / tolta_count if tolta_count > 0 else 0
        if vector_ratio > 0.7 and tolta_count >= 2:
            self.logger.info(f"Node {node.get('name', 'Unnamed')} is a vector composition with {vector_count}/{tolta_count} vector children")
            return True
        return False


    def _is_icon_sized(self, node):
        bounds = node.get('absoluteBoundingBox', {})
        if bounds:
            width = bounds.get('width', 0)
            height = bounds.get('height', 0)
            return (16<=width <=512) and (16<=height <=512)
        return True
    
    def export_nodes_as_images(self, file_key, exportable_nodes):
        self.logger.info(f"Exporting {len(exportable_nodes)} exportable nodes as images")
        headers = {
            "X-Figma-Token": self.api_token
        }
        nodes_to_export = exportable_nodes[:100]

        if len(exportable_nodes) > 100:
            self.logger.warning(f"Only exporting the first 100 exportable nodes due to API limits")
        
        # Filter node IDs to only include those with separators (':' or '-')
        filtered_nodes = []
        for node in nodes_to_export:
            node_id = node.get('id', '')
            if node_id and (':' in node_id or '-' in node_id):
                filtered_nodes.append(node)
            else:
                self.logger.warning(f"Filtering out node without separator in ID: {node.get('name', 'Unnamed')} (ID: {node_id})")
        
        self.logger.info(f"Filtered {len(nodes_to_export)} -> {len(filtered_nodes)} nodes (removed {len(nodes_to_export) - len(filtered_nodes)} without separators)")
        
        if not filtered_nodes:
            self.logger.warning("No valid nodes found after filtering")
            return []
        
        nodes_ids = [node['id'] for node in filtered_nodes]

        ids_param = ','.join(nodes_ids)
        try:
            response = requests.get(
                f"{self.base_url}/images/{file_key}",
                headers=headers,
                params={"ids": ids_param, 'format': 'png', 'scale': 2}
            )
            response.raise_for_status()
            data = response.json()
            images = data.get('images', {})
            urls = []
            for node in filtered_nodes:
                node_id = node['id']
                node_name = node['name']
                if node_id in images and images[node_id]:
                    urls.append({
                        'url': images[node_id],
                        'name': node_name,
                        'id': node_id,
                    })
                    self.logger.info(f"Successfully exported node {node_name} (ID: {node_id}) as image")
                else:
                    self.logger.warning(f"Failed to export node {node_name} (ID: {node_id}) as image")
            self.logger.info(f"Total exportable node images retrieved: {len(urls)}")
            return urls
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to export nodes as images: {str(e)}")
            raise

