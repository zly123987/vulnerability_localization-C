import Structure.Clazz;
import Structure.FileClass;
import Structure.Method;
import com.github.javaparser.StaticJavaParser;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.Modifier;
import com.github.javaparser.ast.Node;
import com.github.javaparser.ast.NodeList;
import com.github.javaparser.ast.body.ClassOrInterfaceDeclaration;
import com.github.javaparser.ast.body.ConstructorDeclaration;
import com.github.javaparser.ast.body.MethodDeclaration;
import com.google.gson.Gson;

import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;

public class CommentsExtractor {

    public static void main(String[] args) throws IOException {
        // First arg is the input file. Second arg is the output file.
        CompilationUnit cu = null;
        String file = args[0];
        String[] tmp = file.split("/");
        String fileName = tmp[tmp.length-1].replace(".java", "");
        FileClass fc = new FileClass();
        try {
            String content = new String(Files.readAllBytes(Paths.get(file)));
            cu = StaticJavaParser.parse(content);
            String fileComments = stripComment(cu.getComment().toString());
            fc.setComment(fileComments);
            fc.setName(fileName);
            for (Node node: cu.getChildNodes()){
                if (node instanceof ClassOrInterfaceDeclaration){
                    Clazz clazz = new Clazz();
                    NodeList<Modifier> modifier = ((ClassOrInterfaceDeclaration) node).getModifiers();
                    clazz.setModifiers(modifier);

                    clazz.setInterface(((ClassOrInterfaceDeclaration) node).isInterface());
                    String classname = ((ClassOrInterfaceDeclaration) node).getName().toString();
                    String classComments = stripComment(node.getComment().toString());
                    clazz.setName(classname);
                    clazz.setComment(classComments);
                    for (Node method: node.getChildNodes()){
                        Method met = new Method();
                        if (method instanceof MethodDeclaration){
                            String methodBody = stripComment(((MethodDeclaration)method).getBody().toString());
                            String methodComment = stripComment(((MethodDeclaration)method).getComment().toString());
                            String methodName = ((MethodDeclaration)method).getNameAsString();
                            String declaration = ((MethodDeclaration) method).getDeclarationAsString();
                            met.setBody(declaration+methodBody);
                            met.setComment( methodComment);
                            met.setName(methodName);
                            clazz.addMethod(met);
                        }
                        if (method instanceof ConstructorDeclaration){
                            String methodBody = stripComment(((ConstructorDeclaration)method).getBody().toString());
                            String methodComment = stripComment(((ConstructorDeclaration)method).getComment().toString());
                            String methodName = ((ConstructorDeclaration)method).getNameAsString();
                            String declaration = ((ConstructorDeclaration) method).getDeclarationAsString();
                            met.setBody(declaration+methodBody);
                            met.setComment( methodComment);
                            met.setName(methodName);
                            clazz.addMethod(met);
                        }
                    }
                    String classBody = ((ClassOrInterfaceDeclaration) node).removeComment().toString();
                    clazz.setBody(classBody);
                    fc.addClass(clazz);
                }

            }
            fc.setBody(cu.removeComment().toString());
            String j = new Gson().toJson(fc);
            Files.writeString(Path.of(args[1]), j,
                    StandardCharsets.UTF_8);

        } catch (IOException e) {
            e.printStackTrace();
            System.err.println("Error on parsing file "+file);
        }

    }

    public static String stripComment(String s){
        return s.replace("Optional.empty", "").replaceFirst("^Optional\\[", "").replaceFirst("\\]$", "");
    }
}
