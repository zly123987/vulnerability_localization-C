package RCL.patterns;
import RCL.Utils.JavaParserUtils;
import com.github.javaparser.JavaParser;
import com.github.javaparser.ParseResult;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.expr.MethodCallExpr;
import RCL.structures.PatchDiff;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.atomic.AtomicReference;

public class ChangedArguments {
    PatchDiff pd;

    public ChangedArguments(PatchDiff dc) {
        pd = dc;
    }

    public Map<String, List<List<String>>> extractInvocations(String codeSnippet) {
        Map<String, List<List<String>>> invocations = new HashMap<>();
        JavaParser parser = new JavaParser();

        ParseResult<CompilationUnit> result = parser.parse(codeSnippet);
        if (!result.isSuccessful()) {
            // Wrap the code snippet in a class and method structure
            String wrappedCode = "class DummyClass { void dummyMethod() { " + codeSnippet + " } }";
            result = parser.parse(wrappedCode);
        }

        result.ifSuccessful(cu -> {
            cu.findAll(MethodCallExpr.class).forEach(mce -> {
                List<String> argsList = new ArrayList<>();
                mce.getArguments().forEach(arg -> argsList.add(arg.toString()));

                invocations.computeIfAbsent(mce.getNameAsString(), k -> new ArrayList<>()).add(argsList);
            });
        });

        return invocations;
    }

    public List<String> compareInvocations() {
        List<String> differingMethods = new ArrayList<>();
        Map<String, List<List<String>>> deletedInvocations = new HashMap<>();
        Map<String, List<List<String>>> addedInvocations = new HashMap<>();



        // Assuming pd.getDiffs() correctly retrieves the diffs
        for (PatchDiff.Diff diff : pd.getDiffs()) {
            // Extract invocations from deleted lines
            diff.getRemovedLines().forEach(line -> {
                Map<String, List<List<String>>> extracted = extractInvocations(line);
                extracted.forEach((method, argsList) -> {
                    if (!deletedInvocations.containsKey(method)) {
                        deletedInvocations.put(method, argsList);
                    } else {
                        deletedInvocations.get(method).addAll(argsList);
                    }
                });
            });

            // Extract invocations from added lines
            diff.getAddedLines().forEach(line -> {
                Map<String, List<List<String>>> extracted = extractInvocations(line);
                extracted.forEach((method, argsList) -> {
                    if (!addedInvocations.containsKey(method)) {
                        addedInvocations.put(method, argsList);
                    } else {
                        addedInvocations.get(method).addAll(argsList);
                    }
                });
            });

            // Compare invocations for methods with the same names but different args
            for (String method : deletedInvocations.keySet()) {
                if (addedInvocations.containsKey(method)) {
                    boolean isDifferent = false;

                    List<List<String>> deletedArgsLists = deletedInvocations.get(method);
                    List<List<String>> addedArgsLists = addedInvocations.get(method);

                    // Check if there's any args list in deletedArgsLists that is not present in addedArgsLists
                    for (List<String> deletedArgs : deletedArgsLists) {
                        if (!addedArgsLists.contains(deletedArgs)) {
                            isDifferent = true;
                            break;
                        }
                    }

                    // Similarly, check if there's any args list in addedArgsLists that is not present in deletedArgsLists
                    for (List<String> addedArgs : addedArgsLists) {
                        if (!deletedArgsLists.contains(addedArgs)) {
                            isDifferent = true;
                            break;
                        }
                    }

                    if (isDifferent && !JavaParserUtils.getBlackList().contains(method)) {
                        differingMethods.add(method);
                    }
                }
            }
        }
        return differingMethods;
    }

}
