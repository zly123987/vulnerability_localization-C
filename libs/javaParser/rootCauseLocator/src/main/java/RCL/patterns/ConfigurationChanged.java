package RCL.patterns;
import RCL.structures.FieldDeclr;
import RCL.structures.PatchDiff;
import com.github.javaparser.JavaParser;
import com.github.javaparser.ParseResult;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.body.FieldDeclaration;
import com.github.javaparser.ast.body.InitializerDeclaration;
import com.github.javaparser.ast.body.VariableDeclarator;
import com.github.javaparser.ast.expr.*;
import com.github.javaparser.ast.stmt.ExpressionStmt;
import com.github.javaparser.ast.visitor.VoidVisitorAdapter;

import java.io.FileInputStream;
import java.nio.file.Paths;
import java.util.*;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.stream.Collectors;

public class ConfigurationChanged {

    private final PatchDiff patchDiff;
    private HashMap<String, VariableDeclarator> newVariableUsages;
    private Set<String> newMethodInvocations;

    public ConfigurationChanged(PatchDiff patchDiff) {
        this.patchDiff = patchDiff;
        this.newVariableUsages = new HashMap<>();
        this.newMethodInvocations = new HashSet<>();
        findPotentialNewUsages();
    }

    private void findPotentialNewUsages() {
        Set<String> identifiersInContextAndRemovedLines = extractIdentifiersFromContextAndRemoved();

        for (PatchDiff.Diff diff : patchDiff.getDiffs()) {
            // Extract removed and context lines
            for (String line : diff.getRemovedLines()) {
                String removedAndContextLinesCombined = line;
                String dummyClassEnclosure = "class Dummy {" + removedAndContextLinesCombined + "  }";
                ParseResult<CompilationUnit> parseResult = new JavaParser().parse(dummyClassEnclosure);
                if (!parseResult.isSuccessful()) {
                    dummyClassEnclosure = "class Dummy { void dummyMethod() { " + removedAndContextLinesCombined + " } }";
                    parseResult = new JavaParser().parse(dummyClassEnclosure);
                }


                // Extract variable usages
                parseResult.ifSuccessful(cu -> {
                    new VoidVisitorAdapter<Void>() {
                        @Override
                        public void visit(NameExpr n, Void arg) {
                            super.visit(n, arg);
                            String name = n.getNameAsString();
                            identifiersInContextAndRemovedLines.add(name);

                        }
                    }.visit(cu, null);
                });

                // Extract method invocations
                parseResult.ifSuccessful(cu -> {
                    new VoidVisitorAdapter<Void>() {
                        @Override
                        public void visit(MethodCallExpr n, Void arg) {
                            super.visit(n, arg);
                            String methodName = n.getNameAsString();

                            identifiersInContextAndRemovedLines.add(methodName);

                        }
                    }.visit(cu, null);
                });

            }
            // Extract new
            for (String line : diff.getAddedLines()) {
                String addedLinesCombined = line;
                String dummyClassEnclosure = "class Dummy {" + addedLinesCombined + "  }";
                ParseResult<CompilationUnit> parseResult = new JavaParser().parse(dummyClassEnclosure);
                if (!parseResult.isSuccessful()) {
                    dummyClassEnclosure = "class Dummy { void dummyMethod() { " + addedLinesCombined + " } }";
                    parseResult = new JavaParser().parse(dummyClassEnclosure);
                }

                // Extract variable usages
                parseResult.ifSuccessful(cu -> {
                    new VoidVisitorAdapter<Void>() {
                        @Override
                        public void visit(NameExpr n, Void arg) {
                            super.visit(n, arg);
                            String name = n.getNameAsString();
                            if (!identifiersInContextAndRemovedLines.contains(name)) {
                                newVariableUsages.put(name, null);
                            }
                        }
                    }.visit(cu, null);
                });

                // Extract method invocations
                parseResult.ifSuccessful(cu -> {
                    new VoidVisitorAdapter<Void>() {
                        @Override
                        public void visit(MethodCallExpr n, Void arg) {
                            super.visit(n, arg);
                            String methodName = n.getNameAsString();
                            if (!identifiersInContextAndRemovedLines.contains(methodName)) {
                                newMethodInvocations.add(n.toString());
                            }
                        }
                    }.visit(cu, null);
                });
            }
        }
    }

    private Set<String> extractIdentifiersFromContextAndRemoved() {
        Set<String> identifiers = new HashSet<>();
        // Implement the extraction logic as before, combining context and removed lines
        // and parsing them to find identifiers (variable names, method names, etc.)
        return identifiers;
    }

    // Getter methods for newVariableUsages and newMethodInvocations if needed
    public HashMap<String, VariableDeclarator> getNewVariableUsages() {
        return newVariableUsages;
    }

    public Set<String> getNewMethodInvocations() {
        return newMethodInvocations;
    }


    public static boolean checkWriteOperation(List<String> lines, String variableName) {
        JavaParser parser = new JavaParser();
        AtomicBoolean writeOperationFound = new AtomicBoolean(false);
        for (String line: lines) {
            if (writeOperationFound.get())
                break;
            // Create a dummy class wrapper
            String classTemplate = "public class DummyClass { %s }";
            String wrappedCode = String.format(classTemplate, line);

            // Parse the wrapped code as a CompilationUnit
            ParseResult<CompilationUnit> result = parser.parse(wrappedCode);
            if (!result.isSuccessful()){
                String methodTemplate = "class DummyClass { void dummyMethod() { %s } }";
                wrappedCode = String.format(methodTemplate, line);

                // Parse the wrapped code as a CompilationUnit
                result = parser.parse(wrappedCode);
            }
            result.ifSuccessful(cu -> {
                cu.accept(new VoidVisitorAdapter<Void>() {
                    @Override
                    public void visit(AssignExpr n, Void arg) {
                        super.visit(n, arg);
                        if (n.getTarget().toString().equals(variableName)) {
                            writeOperationFound.set(true);
                        }
                    }

                    @Override
                    public void visit(VariableDeclarationExpr n, Void arg) {
                        super.visit(n, arg);
                        n.getVariables().forEach(v -> {
                            if (v.getNameAsString().equals(variableName) && v.getInitializer().isPresent()) {
                                writeOperationFound.set(true);
                            }
                        });
                    }

                    @Override
                    public void visit(MethodCallExpr n, Void arg) {
                        super.visit(n, arg);
                        // Check if the scope directly matches the variable name
                        n.getScope().ifPresent(scope -> {
                            if (scope.toString().equals(variableName)) {
                                writeOperationFound.set(true);
                            }
                        });
                        // Additionally, check for nested scopes that might involve the variable
                        if (n.toString().startsWith(variableName + ".")) {
                            writeOperationFound.set(true);
                        }
                    }
                }, null);
            });
        }


            return writeOperationFound.get();
    }
    /**
     * Parses the original files to find definitions or origins of the new variables.
     * @param repoPath The repository path serving as the prefix to diff file paths.
     */
    public List<FieldDeclr> findVariableDefinitions(String repoPath) {
        List<FieldDeclr> ret = new ArrayList<>();
        JavaParser javaParser = new JavaParser();
        for (String variable : newVariableUsages.keySet()) {
            String FieldType = variable;

            for (PatchDiff.Diff diff : patchDiff.getDiffs()) {
                List<String> addedLines = diff.getAddedLines();
                // Assuming the original file path can be derived or is known. Adjust accordingly.
                String originalFilePath = repoPath + patchDiff.getNew_file_path();
                try (FileInputStream in = new FileInputStream(Paths.get(originalFilePath).toFile())) {
                    ParseResult<CompilationUnit> result = javaParser.parse(in);
                    // static
                    result.ifSuccessful(cu -> {
                        cu.findAll(InitializerDeclaration.class).forEach(initializer -> {
                            if (initializer.isStatic()) {
//                                System.out.println("Found a static initializer in: " + originalFilePath);
                                // If you need to check for specific variable declarations within the static block:
                                initializer.findAll(VariableDeclarationExpr.class).forEach(vde -> {
                                    if (vde.getVariables().stream().anyMatch(v -> v.getNameAsString().equals(variable))) {
                                        String variableType = vde.getVariables().stream().filter(v -> v.getNameAsString().equals(variable)).collect(Collectors.toList()).get(0).getType().asString();
                                        String declaredClass = cu.getTypes().get(0).getNameAsString();
                                        if (checkWriteOperation(addedLines, variable)){
                                            if (!ret.toString().contains(variable))
                                                ret.add(new FieldDeclr(variable, variableType, declaredClass, true));
                                        }
                                    }
                                    // Here you can further analyze the variable declarations,
                                    // e.g., to check names, types, or initialization values.
                                });
                            }
                        });
                    });
                    // field
                    result.ifSuccessful(cu -> {
                        cu.findAll(VariableDeclarator.class).forEach(var -> {
                            if (var.getNameAsString().equals(variable)) {
                                var.findAncestor(FieldDeclaration.class).ifPresent(field -> {
                                    // If this condition is true, the variable is a field in the class.
                                    String variableType = var.getType().asString();
                                    String declaredClass = cu.getTypes().get(0).getNameAsString();
                                    if (checkWriteOperation(addedLines, variable)) {
                                        if (!ret.toString().contains(variable))
                                            ret.add(new FieldDeclr(variable, variableType, declaredClass, false));
                                    }
//                                    System.out.println("Variable " + variable + " is a field in: " + originalFilePath);
                                    // Here, you don't distinguish between static or non-static.
                                    // All that matters is that it's a field.
                                });
                            }
                        });
                    });

                    // Special case for setFeature
                    result.ifSuccessful(cu -> {
                        cu.findAll(VariableDeclarator.class).forEach(var -> {
                            if (var.getNameAsString().equals(variable)) {

                                // If this condition is true, the variable is a field in the class.
                                String variableType = var.getType().asString();
                                String declaredClass = cu.getTypes().get(0).getNameAsString();
                                for (String method: newMethodInvocations) {
                                    if (method.contains(variable + ".setFeature")) {
                                        ret.add(new FieldDeclr(variable, variableType, declaredClass, false));
                                        break;
                                    }
                                }

                            }
                        });
                    });
                } catch (Exception e) {
                    e.printStackTrace();
                }
            }

        }
        return ret;
    }

    public String determineConfigRelated(){
        // Check if the va
        String ret = "";
        if (newVariableUsages.size() > 0){
            // Check if Config word in side variable name
            for (String variable : newVariableUsages.keySet()){


                if (variable.toLowerCase().contains("config")){
                    ret = variable;
                }
            }
        }
        if (newMethodInvocations.size() > 0) {
            // Check if Config word in side method name
            for (String method : newMethodInvocations){
                if (method.toLowerCase().contains("config")){
                    ret = method;
                }
            }
        }
        return ret;
    }
}
