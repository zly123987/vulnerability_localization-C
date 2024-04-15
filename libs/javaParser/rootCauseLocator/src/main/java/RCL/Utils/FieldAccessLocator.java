package RCL.Utils;

import RCL.structures.FieldDeclr;
import com.github.javaparser.JavaParser;
import com.github.javaparser.ParseResult;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.body.ClassOrInterfaceDeclaration;
import com.github.javaparser.ast.body.FieldDeclaration;
import com.github.javaparser.ast.body.MethodDeclaration;
import com.github.javaparser.ast.expr.AssignExpr;
import com.github.javaparser.ast.expr.FieldAccessExpr;
import com.github.javaparser.ast.expr.NameExpr;
import com.github.javaparser.ast.visitor.VoidVisitorAdapter;

import java.io.File;
import java.io.FileInputStream;
import java.util.HashSet;
import java.util.Set;

public class FieldAccessLocator {

    private Set<String> readAccesses = new HashSet<>();
    private Set<String> writeAccesses = new HashSet<>();
    private String fieldName;
    private String fieldDeclaringClass;

    public FieldAccessLocator(String fieldName, String fieldDeclaringClass) {
        this.fieldName = fieldName;
        this.fieldDeclaringClass = fieldDeclaringClass;
    }

    public void analyzeRepository(File directory) {
        if (directory.isDirectory()) {
            for (File file : directory.listFiles()) {
                if (file.isDirectory()) {
                    analyzeRepository(file); // Recursive call for subdirectories
                } else if (file.getName().endsWith(".java")) {
                    analyzeJavaFile(file);
                }
            }
        }
    }

    private void analyzeJavaFile(File file) {
        JavaParser javaParser = new JavaParser();
        try (FileInputStream in = new FileInputStream(file)) {
            ParseResult<CompilationUnit> result = javaParser.parse(in);
            result.ifSuccessful(cu -> {
                cu.accept(new VoidVisitorAdapter<Void>() {
                    @Override
                    public void visit(FieldAccessExpr fae, Void arg) {
                        super.visit(fae, arg);
                        if (fae.getNameAsString().equals(fieldName) && fae.getScope().toString().contains(fieldDeclaringClass)) {
                            // Assuming direct field access implies a read operation
                            readAccesses.add(fae.toString());
                        }
                    }

                    @Override
                    public void visit(AssignExpr ae, Void arg) {
                        super.visit(ae, arg);
                        if (ae.getTarget() instanceof NameExpr) {
                            NameExpr nameExpr = (NameExpr) ae.getTarget();
                            if (nameExpr.getNameAsString().equals(fieldName)) {
                                // This might be a write operation to the field, add additional checks if necessary
                                writeAccesses.add(nameExpr.toString());
                            }
                        }
                    }
                }, null);
            });
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public Set<String> getReadAccesses() {
        return readAccesses;
    }

    public Set<String> getWriteAccesses() {
        return writeAccesses;
    }

    // Example usage
    public static void getAccess(FieldDeclr fieldDeclr, String repoPath) {
        FieldAccessLocator locator = new FieldAccessLocator(fieldDeclr.getName(), fieldDeclr.getDeclardClass());
        locator.analyzeRepository(new File(repoPath));
        System.out.println("Field Read Accesses: " + locator.getReadAccesses());
        System.out.println("Field Write Accesses: " + locator.getWriteAccesses());
    }
}
