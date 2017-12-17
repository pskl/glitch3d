import rna_xml
import xml.dom.minidom
import xml.etree.ElementTree as ET

# Retrieve XML fixture and create new node tree
def fetch_material(name):
    try:
        return MATERIALS['name']
    except KeyError:
        material_path = MATERIALS_PATH + name + '.xml'
        # xml_nodes = ET.parse(material_path)
        xml_nodes = xml.dom.minidom.parse(material_path)
        # xml_nodes = xml.dom.minidom.parseString(open(material_path).read())
        material = create_cycles_material(name, clean=True)
        # result = [item for item in xml_nodes.chilNodes[0] if item.nodeType == xml.dom.minidom.Node.ELEMENT_NODE]
        root = xml_nodes.getElementsByTagName("ShaderNodeTree")[0]
        # root = xml_nodes.getroot()
        # code.interact(local=dict(globals(), **locals()))
        purge_xml(root)
        tree = bpy.data.node_groups.new(name, type='ShaderNodeTree')
        rna_xml.xml2rna(root, root_rna=bpy.data.node_groups[-1])
        print(bpy.data.node_groups[-1].nodes)
        sys.exit()
        group_node = material.node_tree.nodes.new('ShaderNodeGroup')
        group_node.node_tree = bpy.data.node_groups[-1]
        MATERIALS['name'] = material
        return material

# Save material to new xml file (local helper, do not run in production)
def serialize_material(obj, name):
    print("Serializing node tree")
    path = MATERIALS_PATH + name + '.xml'
    f = open(MATERIALS_PATH + name + '.xml',"w+")
    rna_xml.rna2xml(fw=f.write, root_node="Root", root_rna=obj.data.materials[-1].node_tree, method='DATA')
    f.close()
    return path

# Remove text nodes
def purge_xml(tree):
    for node in tree.childNodes[:]: # work on copy of list
        if node.nodeType != xml.dom.minidom.Node.ELEMENT_NODE:
            node.parentNode.removeChild(node)
        else:
            purge_xml(node)