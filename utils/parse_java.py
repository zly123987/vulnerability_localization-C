import json
import re
import os


def parse_java_for_variable(java_file, clazz_name):
    os.system('java -jar libs/javaParser-Variable.jar '+java_file+' '+clazz_name+'_tempParsedResult.json')
    with open(clazz_name+'_tempParsedResult.json') as f:
        result = json.load(f)
        os.remove(clazz_name+'_tempParsedResult.json')
        return result

def parse_java(java_file, clazz_name):
    try:
        os.system('java -jar libs/javaParser-1.0-SNAPSHOT-jar-with-dependencies.jar '+java_file+' '+clazz_name+'_tempParsedResult.json')
        with open(clazz_name+'_tempParsedResult.json') as f:
            result = json.load(f)
            os.remove(clazz_name+'_tempParsedResult.json')
            return result
    except:
        print('Error in parsing:', java_file)
    return None
    

# def get_method_info(file_path):
#     methods = []
#     # Create a PlyJ parser
#     parser = plyj.Parser()

#     # Parse the Java file
#     tree = parser.parse_file(file_path)
#     if not tree:
#         return []
#     # Iterate over all type declarations (classes, interfaces, etc.)
#     for type_decl in tree.type_declarations:
#         # Iterate over all body declarations (fields, methods, etc.)
#         for body_decl in type_decl.body:
#             # Check if the body declaration is a method
#             if isinstance(body_decl, plyj.MethodDeclaration):
#                 # Print the method signature
#                 modifier = ' '.join(m for m in body_decl.modifiers if isinstance(m, str))
#                 return_type = body_decl.return_type if body_decl.return_type else 'void'
#                 if type(return_type) is not str:
#                     if type(return_type.name) is str:
#                         return_type = return_type.name
#                     else:
#                         return_type = return_type.name.value

#                 name = body_decl.name
#                 parameters = []
#                 for p in body_decl.parameters:
#                     # res = re.search('Name\(value=\'(.*?)\'', p.type.name)
#                     # if res:
#                     #     type = res.group(1)
#                     # else:
#                     #     type = p.type
#                     # res = re.search('Variable\(name=\'(.*?)\'', p.variable)
#                     # if res:
#                     #     variable = res.group(1)
#                     # else:
#                     #     variable = p.variable

#                     if type(p.type) is str:
#                         parameters.append({'type': p.type, 'variable': p.variable.name})
#                     else:
#                         if type(p.type.name) is str:
#                             parameters.append({'type': p.type.name, 'variable': p.variable.name})
#                         else:
#                             parameters.append({'type':p.type.name.value, 'variable':p.variable.name})

#                 # print(f"{modifier} {return_type} {name}({parameters})")
#                 methods.append({
#                     'modifier': modifier,
#                     'return_type': return_type,
#                     'name': name,
#                     'parameters': parameters
#                 })
#     return methods
# # You can replace 'YourJavaFile.java' with your actual java file path




# def remove_method_bodies_and_comments(data):


#     # remove single-line comments
#     data = re.sub(r'//.*', '', data)

#     # remove multi-line comments
#     data = re.sub(r'/\*.*?\*/', '', data, flags=re.DOTALL)

#     # remove import statements
#     data = re.sub(r'import\s+.*;\n', '', data)

#     lines = data.split('\n')

#     inside_method = False
#     nested_level = 0
#     result = []

#     for line in lines:

#         if '{' in line:
#             nested_level += 1
#         if '}' in line:
#             nested_level -= 1

#         if re.search(r'\s*\bpublic\b|\bprivate\b|\bprotected\b.*\(', line):
#             inside_method = True

#         # If inside a method and nested level is greater than 1, don't add the line to the result
#         if inside_method and nested_level > 1:
#             continue
#         else:
#             result.append(line)

#         if inside_method and nested_level == 1 and '}' in line:
#             inside_method = False
#     tmp = []
#     for each in result:
#         if not re.match('^\s*$', each):
#             tmp.append(each)
#     result_data = '\n'.join(tmp)

#     return result_data

# if __name__=='__main__':
#     # You can replace 'YourJavaFile.java' with your actual java file path
#     print(remove_method_bodies_and_comments('/Users/XXX/workspace/maven_repos/logging-log4j2/log4j-jdbc-dbcp2/src/main/java/org/apache/logging/log4j/core/appender/db/jdbc/PoolingDriverConnectionSource.java'))
#     print(get_method_signatures('/Users/XXX/workspace/maven_repos/logging-log4j2/log4j-jdbc-dbcp2/src/main/java/org/apache/logging/log4j/core/appender/db/jdbc/PoolingDriverConnectionSource.java'))