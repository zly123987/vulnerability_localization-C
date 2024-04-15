package RCL.patterns;
import RCL.Utils.JavaParserUtils;
import RCL.structures.PatchDiff;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class ReplacedInvocation {
    private final PatchDiff pd;

    public ReplacedInvocation(PatchDiff pd) {
        this.pd = pd;
    }

    public List<Map<String, String>> findReplacedInvocations() {
        List<Map<String, String>> allReplacedInvocations = new ArrayList<>();

        for (PatchDiff.Diff diff : pd.getDiffs()) {
            Map<String, String> replacedInvocations = new HashMap<>();
            Map<String, List<String>> removedInvocations = JavaParserUtils.extractInvocationsAndInitializations(diff.getRemovedLines());
            Map<String, List<String>> addedInvocations = JavaParserUtils.extractInvocationsAndInitializations(diff.getAddedLines());

            // Compare invocations by arguments
            removedInvocations.forEach((removedMethodName, removedArgsList) -> {
                addedInvocations.forEach((addedMethodName, addedArgsList) -> {
                    if (!removedMethodName.equals(addedMethodName) && removedArgsList.size()==addedArgsList.size()
                            && !JavaParserUtils.getBlackList().contains(removedMethodName)) {
                        // If the arguments match but the method names are different, record the change
                        replacedInvocations.put(removedMethodName, addedMethodName);
//                        System.out.println("Replaced Invocation Detected:");
//                        System.out.println("Method Name: " + removedMethodName);
//                        System.out.println("Removed From: " + diff.getRemovedLines());
//                        System.out.println("Added To: " + diff.getAddedLines());
                    }
                });
            });

            if (!replacedInvocations.isEmpty()) {
                allReplacedInvocations.add(replacedInvocations);
            }
        }

        return allReplacedInvocations;
    }
}
