from scipy.io import loadmat
from lxml import etree as ET

# 读取MAT文件
mat = loadmat('gatewayList1_xy.mat')
selected_APs = mat['nodes_cartesian']

# 输出文件路径
output_path = 'gatewayList1.add.xml'

# 创建XML根节点
root = ET.Element('additional')

# 为每个中继节点位置创建一个POI元素
for index, (x, y) in enumerate(selected_APs):
    # 设置颜色为指定的浅蓝色，半透明
    ET.SubElement(root, 'poi', id=f'ap_{index}', x=str(x), y=str(y), color='green', type='rsu')

# 将生成的XML内容保存到文件
tree = ET.ElementTree(root)
tree.write(output_path, pretty_print=True, xml_declaration=True, encoding='UTF-8')