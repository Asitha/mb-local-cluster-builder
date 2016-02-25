import ConfigParser
import zipfile
import shutil
import os
import xml.etree.ElementTree as ET
import yaml

DEFAULT_SECTION = 'default'
CONST_HOSTNAME = 'hostname'
CONST_CLUSTER_DIR = 'clusterPath'
CONST_PACK_LOCATION = 'mbPackLocation'
CONST_SQL_JAR_LOCATION = 'sqlJarLocation'
CONST_NODE_COUNT = 'nodeCount'

# Read configurations
config = ConfigParser.ConfigParser()
config.read('c5Conf.ini')

hostname = config.get(DEFAULT_SECTION, CONST_HOSTNAME)
clusterDir = config.get(DEFAULT_SECTION, CONST_CLUSTER_DIR)
mbPackLocation = config.get(DEFAULT_SECTION, CONST_PACK_LOCATION)
sqlJarLocation = config.get(DEFAULT_SECTION, CONST_SQL_JAR_LOCATION)
nodeCount = config.get(DEFAULT_SECTION, CONST_NODE_COUNT)

print 'host ' + hostname
print 'path ' + clusterDir
print 'packLoc ' + mbPackLocation

print "Extracting file " + mbPackLocation + " into " + clusterDir
with zipfile.ZipFile(mbPackLocation, 'r') as z:
    z.extractall(clusterDir)
    orig_filename = z.infolist()[0].filename.replace(os.path.sep, '')
print "Extracted pack into " + clusterDir

confDir = clusterDir + os.path.sep + orig_filename + os.path.sep + "conf"
brokerXMLDir = confDir + os.path.sep + "broker.xml"

brokerXMLTree = ET.parse(brokerXMLDir)
brokerXMLTree.findall('./coordination/thriftServerHost')[0].text = hostname
brokerXMLTree.write(brokerXMLDir)
shutil.copy2("master-datasources.xml", confDir + os.path.sep + "datasources")
jarDstDir = clusterDir + os.path.sep + orig_filename + os.path.sep + "osgi" + os.path.sep + "dropins"
shutil.copy2(sqlJarLocation, jarDstDir)

for x in range(0, int(nodeCount)):
    destDir = clusterDir + os.path.sep + "mb" + str(x+1)
    shutil.copytree(clusterDir + os.path.sep + orig_filename, destDir)
    carbonYamlPath = destDir + os.path.sep + 'conf' + os.path.sep + 'carbon.yml'
    stream = file(carbonYamlPath, 'r')
    carbonYaml = yaml.load(stream)
    carbonYaml['ports']['offset'] = x
    with open(carbonYamlPath, 'w') as yamlFile:
        yamlFile.write(yaml.dump(carbonYaml, default_flow_style=False))



