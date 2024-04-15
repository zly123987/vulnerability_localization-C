
import RCL.Utils.FieldAccessLocator;
import RCL.patterns.*;
import RCL.structures.FieldDeclr;
import com.google.gson.Gson;
import com.google.gson.reflect.TypeToken;
import java.io.FileReader;
import java.lang.reflect.Type;
import java.util.*;

import RCL.structures.PatchDiff;
public class DiffParser {
    public static void main(String[] args) {
        String cve = args[0];
        String repoPath = args[1];
        String jsonPath = args[2];
        try {
            List<String> result = new ArrayList<>();
            Gson gson = new Gson();
            Type diffChangeListType = new TypeToken<List<PatchDiff.DiffChange>>(){}.getType();
            List<PatchDiff.DiffChange> changes = gson.fromJson(new FileReader(jsonPath), diffChangeListType);
            PatchDiff pd = new PatchDiff(changes);
            ChangedArguments changeArgTester = new ChangedArguments(pd);
            ReplacedInvocation replacedInvocation = new ReplacedInvocation(pd);
            ConfigurationChanged configurationChanged = new ConfigurationChanged(pd);
            result = changeArgTester.compareInvocations();
            // deduplicate result
            result = deduplicateList(result);


            List<Map<String, String>> replacedInvocationResult = replacedInvocation.findReplacedInvocations();
            List<FieldDeclr> fields = configurationChanged.findVariableDefinitions(repoPath);
            RemovedMethod removedMethodChecker = new RemovedMethod(pd);
            removedMethodChecker.detectChanges();
//            for (FieldDeclr field : fields) {
//                System.out.println(field);
//                FieldAccessLocator.getAccess(field, repoPath);
//            }

//            String related = configurationChanged.determineConfigRelated();
//            StaticConfigAdded staticConfigAdded = new StaticConfigAdded(pd);
//            String addedField = staticConfigAdded.findAddedField();
            if (!(result.size() ==0)) {
                System.out.println("Final result:" + String.join("|",result) + ", Arguments changed");
                return;
            }
            List<String> replacedInvocationNames = new ArrayList<>();
            for (Map<String, String> stringStringMap : replacedInvocationResult) {
                // extend replacedInvocationNames
                for (String key: stringStringMap.keySet()){
                    replacedInvocationNames.addAll(Collections.singleton(key));
                }
            }
            if (!replacedInvocationResult.isEmpty()) {
                System.out.println("Final result:" + String.join("|", replacedInvocationNames) + ", Replaced invocation");
                return;
            }

            if (!fields.isEmpty()) {
                // Join each field getName()
                String names = fields.stream()
                        .map(FieldDeclr::getName)
                        .reduce((s1, s2) -> s1 + "|" + s2)
                        .orElse("");
                System.out.println("Final result:" + names + ", Configuration changed");
                return;
            }
//            if (!addedField.equals("")) {
//                System.out.println("Final result:" + addedField + ", Static config added");
//                return;
//            }

            if (removedMethodChecker.getRemoveMethodName().size()>0) {
                System.out.println("Final result:" + String.join("|",deduplicateList(removedMethodChecker.getRemoveMethodName())) + ", Removed method");
                return;
            }
            if (removedMethodChecker.getDeprecatedMethodName().size()>0) {
                System.out.println("Final result:" + String.join("|", deduplicateList(removedMethodChecker.getDeprecatedMethodName())) + ", Deprecated method");
                return;
            }
            System.out.println("Final result: No pattern found");
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public static List<String> deduplicateList(List<String> listWithDuplicates) {
        // Use LinkedHashSet to remove duplicates and maintain the order
        Set<String> setWithoutDuplicates = new LinkedHashSet<>(listWithDuplicates);

        // Convert the set back to list
        return new ArrayList<>(setWithoutDuplicates);
    }
}

