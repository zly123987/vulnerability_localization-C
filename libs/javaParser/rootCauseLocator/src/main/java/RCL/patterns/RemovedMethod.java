package RCL.patterns;

import RCL.structures.PatchDiff;
import com.github.javaparser.JavaParser;
import com.github.javaparser.ParseResult;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.body.MethodDeclaration;
import com.github.javaparser.ast.visitor.VoidVisitorAdapter;

import javax.swing.*;
import java.util.ArrayList;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.List;

public class RemovedMethod {

    private PatchDiff patchDiff;
    private List<String> removeMethodName = new ArrayList<>();
    private List<String> deprecatedMethodName = new ArrayList<>();
    private boolean isDeprecatedDetected = false; // Flag to indicate if @Deprecated was detected in the previous diff
    public RemovedMethod(PatchDiff patchDiff) {
        this.patchDiff = patchDiff;
    }

    public void detectChanges() {
        for (PatchDiff.Diff diff : patchDiff.getDiffs()) {
            detectRemovedMethods(diff.getRemovedLines());
            // If @Deprecated was detected in the added lines of the previous diff
            if (isDeprecatedDetected) {
                // Process the current diff's context lines to find the method name
                if (!diff.getContextLines().isEmpty()) {
                    String relatedMethodSignature = diff.getContextLines().get(0);
                    String methodName = extractMethodName(relatedMethodSignature);
                    if (!methodName.isEmpty()) {
                        deprecatedMethodName.add(methodName);
                    }
                }
                isDeprecatedDetected = false; // Reset the flag after processing
            }

            // Check current diff's added lines for @Deprecated
            String addedCode = String.join("\n", diff.getAddedLines());
            if (addedCode.toLowerCase().contains("deprecate")|| addedCode.toLowerCase().contains("deprecation")) {
                isDeprecatedDetected = true; // Set the flag if @Deprecated is found
            }
        }
    }

    private void detectRemovedMethods(List<String> removedLines) {
        // Join all removed lines into a single String
        String removedCode = String.join("\n", removedLines);

        // Wrap the removed code in a dummy class to parse it
        String classWrapper = "class DummyClass { " + removedCode + " }";
        JavaParser parser = new JavaParser();
        ParseResult<CompilationUnit> result = parser.parse(classWrapper);

        result.ifSuccessful(cu -> {
            cu.accept(new VoidVisitorAdapter<Void>() {
                @Override
                public void visit(MethodDeclaration n, Void arg) {
                    super.visit(n, arg);
                    removeMethodName.add(n.getSignature().getName());
                }
            }, null);
        });
    }


    private String extractMethodName(String methodSignature) {
        // Regex pattern to extract method name from a declaration
        Pattern pattern = Pattern.compile("\\s+([\\w\\d_]+)\\s*\\(");
        Matcher matcher = pattern.matcher(methodSignature);
        if (matcher.find()) {
            return matcher.group(1);
        }
        return "";
    }

    public List<String> getRemoveMethodName() {
        return removeMethodName;
    }

    public List<String> getDeprecatedMethodName() {
        return deprecatedMethodName;
    }
}
