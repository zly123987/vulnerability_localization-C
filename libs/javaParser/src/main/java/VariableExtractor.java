import Structure.Clazz;
import Structure.FileClass;
import Structure.Method;
import com.github.javaparser.StaticJavaParser;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.Modifier;
import com.github.javaparser.ast.Node;
import com.github.javaparser.ast.NodeList;
import com.github.javaparser.ast.body.ClassOrInterfaceDeclaration;
import com.github.javaparser.ast.body.MethodDeclaration;
import com.github.javaparser.ast.body.VariableDeclarator;
import com.github.javaparser.ast.expr.SimpleName;
import com.github.javaparser.ast.expr.VariableDeclarationExpr;
import com.github.javaparser.ast.visitor.VoidVisitorAdapter;
import com.google.gson.Gson;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Set;

public class VariableExtractor {

    public static void main(String[] args) throws IOException {
        CompilationUnit cu = null;
        String file = args[0];
        String[] tmp = file.split("/");
        String fileName = tmp[tmp.length - 1].replace(".java", "");
        FileClass fc = new FileClass();
        try {
            String content = new String(Files.readAllBytes(Paths.get(file)));
            cu = StaticJavaParser.parse(content);
            String fileComments = stripComment(cu.getComment().toString());
            fc.setComment(fileComments);
            fc.setName(fileName);
            new VoidVisitorAdapter<Object>() {
                @Override
                public void visit(ClassOrInterfaceDeclaration cid, Object arg) {
                    super.visit(cid, arg);
                    Clazz clazz = new Clazz();
                    // Initialize var_def and var_use for the class
                    NodeList<Modifier> modifier = cid.getModifiers();
                    clazz.setModifiers(modifier);

                    clazz.setInterface(cid.isInterface());
                    String classname = (cid.getName().toString());
//                    String classComments = stripComment(cid.toString());
                    clazz.setName(classname);
//                    clazz.setComment(classComments);
                    // Visit variable declarations and usages within the class


                    for (Node method : cid.getChildNodes()) {
                        if (method instanceof MethodDeclaration) {
                            Method met = new Method();
                            String methodBody = stripComment(((MethodDeclaration)method).getBody().toString());
//                            String methodComment = stripComment((method).getComment().toString());
                            String methodName = ((MethodDeclaration)method).getNameAsString();
                            String declaration = ((MethodDeclaration) method).getDeclarationAsString();
                            met.setBody(declaration+methodBody);
//                            met.setComment( methodComment);
                            met.setName(methodName);
                            // Visit variable declarations and usages within the method
                            visitVariableDeclarationsAndUsages((MethodDeclaration) method, met.getVarDef(), met.getVarRef());

                            clazz.addMethod(met);
                        }
                    }
                    visitVariableDeclarationsAndUsages(cid, clazz.getVarDef(), clazz.getVarRef());


                    fc.addClass(clazz);
                }
            }.visit(cu, null);

            String j = new Gson().toJson(fc);
            Files.writeString(Path.of(args[1]), j, StandardCharsets.UTF_8);

        } catch (IOException e) {
            e.printStackTrace();
            System.err.println("Error on parsing file " + file);
        }
    }

    private static void visitVariableDeclarationsAndUsages(Node node, Set<String> varDef, Set<String> varUse) {
        node.walk(VariableDeclarationExpr.class, vde -> {
            for (VariableDeclarator var : vde.getVariables()) {
                varDef.add(var.getNameAsString());
            }
        });
        node.walk(SimpleName.class, sn -> {
            // Only add to varUse if it's not already in varDef to avoid counting declarations as usages
            if (!varDef.contains(sn.getIdentifier())) {
                varUse.add(sn.getIdentifier());
            }
        });
    }

    public static String stripComment(String s) {
        return s.replace("Optional.empty", "").replaceFirst("^Optional\\[", "").replaceFirst("\\]$", "");
    }
}
