import xml.etree.ElementTree as ET

def parse_pom(file_path):
    try:
        # Parse the XML file
        tree = ET.parse(file_path)

        # Get the root of the XML tree
        root = tree.getroot()

        # Create dictionary to hold extracted values
        data = {}

        # Define namespaces
        namespaces = {'maven': 'http://maven.apache.org/POM/4.0.0'}

        # Extract the groupId, artifactId, and version
        for element in root.findall('maven:groupId', namespaces):
            data['groupId'] = element.text
        for element in root.findall('maven:artifactId', namespaces):
            data['artifactId'] = element.text
        for element in root.findall('maven:version', namespaces):
            data['version'] = element.text

        # If groupId, artifactId, or version not found at root level, look for them inside 'parent' element
        if 'groupId' not in data or 'artifactId' not in data or 'version' not in data:
            for parent in root.findall('maven:parent', namespaces):
                if 'groupId' not in data:
                    for element in parent.findall('maven:groupId', namespaces):
                        data['groupId'] = element.text
                if 'artifactId' not in data:
                    for element in parent.findall('maven:artifactId', namespaces):
                        data['artifactId'] = element.text
                if 'version' not in data:
                    for element in parent.findall('maven:version', namespaces):
                        data['version'] = element.text

        return data

    except ET.ParseError as e:
        print(f"Failed to parse XML: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

if __name__=='__main__':
    # Test the function
    file_path = "pom.xml"
    data = parse_pom(file_path)

    if data is not None:
        print(f"groupId: {data.get('groupId')}")
        print(f"artifactId: {data.get('artifactId')}")
        print(f"version: {data.get('version')}")
