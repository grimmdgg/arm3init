#!/usr/bin/python
'''
Created on Mar 12, 2013



@author: reaper
'''

import optparse
import xml.etree.ElementTree as ET
import re
import urllib
import sys

defaultURL="http://browser.six-projects.net/cfg_weapons/classlist?utf8=%E2%9C%93&version=67&commit=xml&options%5Bgroup_by%5D=weap_type&options%5Bcustom_type%5D=&options%5Bfaction%5D="

def __strip_non_ascii(string):
    
        stripped = (c for c in string if 0 < ord(c) < 127)
        return ''.join(stripped)
    
def __get_magazines(element):
    magazinesnames=[]
    muzzles = element.find('muzzles')
    for muzzle in muzzles.findall('muzzle'):
        magazines = muzzle.find('magazines')
        for magazine in magazines.findall('magazine'):
            magazinesnames.append(magazine.find('name').text)
            
    return magazinesnames
    

def __processObject(type, options):
    returnValue = True
    if (type == 'Item'):
        if (options.item == False and options.all == False):
            returnValue = False
    elif (type == 'Rifle'):
        if (options.rifle == False and options.all == False):
            returnValue = False
    elif (type == 'Vehicle'):
        if (options.vehicle == False and options.all == False):
            returnValue = False
    elif (type == 'Equip'):
        if (options.equip == False and options.all == False):
            returnValue = False
    elif (type == 'Pistol'):
        if (options.pistol == False and options.all == False):
            returnValue = False
    elif (type == 'Launcher'):
        if (options.launcher == False and options.all == False):
            returnValue = False
    elif (type == 'Special'):
        if (options.special == False and options.all == False):
            returnValue = False
            
    return returnValue

def main():
    parser = optparse.OptionParser("USAGE: ArmaConfig [options] {-d datafilepath|-u datafileurl} Item_name [Item_name]")
    parser.add_option("--weapon_number",type="int",dest="weapon_number",default=5,help="Number of each weapon type to add")
    parser.add_option("--magazine_number",type="int",dest="magazine_number",default=5,help="Number of each magazine type per weapon to add")
    parser.add_option("--item_number",type="int",dest="item_number",default=5,help="Number of each item type to add")
    parser.add_option("-d","--data_file",type="string",dest="data_file_path",help="Datafile (xml) path")
    parser.add_option("-u","--data_url",type="string",dest="data_url",default=defaultURL,help="Datafile (xml) url")
    parser.add_option("-l","--list",action="store_true",default=False,dest="list",help="List object names")
    parser.add_option("-v","--verbose",action="store_true",default=False,dest="verbose",help="List verbose info on each object")
    parser.add_option("--init",action="store_true",default=False,dest="print_config",help="Print the text used in the arma init script")
    parser.add_option("-i","--infile",type="string",dest="infile",help="File containing items names to process")
    parser.add_option("-r","--regex",type="string",dest="regex",help="Perform actions on all object that match a regular expression")
    parser.add_option("--all_types",action="store_true",default=False,dest="all",help="Perform actions on all object types")
    parser.add_option("--rifle",action="store_true",default=False,dest="rifle",help="Perform actions on objects of type 'Rifle'")
    parser.add_option("--vehicle",action="store_true",default=False,dest="vehicle",help="Perform actions on objects of type 'Vehicle")
    parser.add_option("--item",action="store_true",default=False,dest="item",help="Perform actions on objects of type 'Item'")
    parser.add_option("--equip",action="store_true",default=False,dest="equip",help="Perform actions on objects of type 'Equip'")
    parser.add_option("--pistol",action="store_true",default=False,dest="pistol",help="Perform actions on objects of type 'Pistol'")
    parser.add_option("--special",action="store_true",default=False,dest="special",help="Perform actions on objects of type 'Special'")
    parser.add_option("--launcher",action="store_true",default=False,dest="launcher",help="Perform actions on objects of type 'Launcher'")
    
    (options,args)=parser.parse_args()
    
    root=None
    
    if (options.data_file_path):
        tree = ET.parse(options.data_file_path)
        root = tree.getroot()
    else:
        
        try:
            urlfh = urllib.urlopen(options.data_url)
            root = ET.fromstringlist(urlfh.readlines())
        except Exception:
            print ("Error: failed to retrieve data from URL")
            sys.exit()
        finally:
            urlfh.close()
    
    gearToProcess=[]
    for arg in args:
        gearToProcess.append(arg)
    
    if(options.infile):
        try:
            fh = open(options.infile,'r')
            for line in fh:
                gearToProcess.append(line.strip())
        except Exception:
            pass
        finally:
            fh.close()
        
    
    
    for object in root.iter('object'):
      
        magazines=__get_magazines(object)
        type=object.find('type').text
        name=object.find('name').text
        
        if (options.regex and re.search(options.regex,name,flags=0)):
            gearToProcess.append(name)
        
        if (name in gearToProcess):
            pass
        elif(__processObject(type, options)==False):
            continue
            
        if(options.list):
            print (name)
            
        if(options.list and options.verbose):
            displayname=object.find('displayname').text
            
            try:
                if(displayname):
                    print("Display Name:"+displayname)
            except UnicodeEncodeError:
                    print(__strip_non_ascii("Display Name:"+displayname))
                    
                        
            if(type):
                print("Object Type:"+type)
                
            if(len(magazines)>0):
                print("Magazines: "+str.join(",",magazines))
            print("\n")
            
        if(options.print_config):
            if(type=='Item' or type=='Equip'):
                print(str.format("this additemcargo [\"{0}\", {1}];",name,options.item_number))
            if(type=='Rifle' or type=='Pistol' or type =='Launcher'):
                print (str.format("this addweaponcargo [\"{0}\", {1}];",name,options.weapon_number))
                
                for magazine in magazines:
                    print  (str.format("this addmagazinecargo [\"{0}\", {1}];",magazine,options.weapon_number * options.magazine_number))
        
            
            
                        
if __name__ == '__main__':
    
    main()