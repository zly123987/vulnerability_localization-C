package RCL.patterns;

import RCL.structures.PatchDiff;
import com.github.javaparser.JavaParser;
import com.github.javaparser.ParseResult;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.body.FieldDeclaration;
import com.github.javaparser.ast.visitor.VoidVisitorAdapter;

public class StaticConfigAdded {

    private final PatchDiff patchDiff;

    public StaticConfigAdded(PatchDiff patchDiff) {
        this.patchDiff = patchDiff;
    }

    public String findAddedField() {
        for (PatchDiff.Diff diff : patchDiff.getDiffs()) {
            String addedLinesCombined = String.join("\n", diff.getAddedLines());
            ParseResult<CompilationUnit> parseResult = new JavaParser().parse(addedLinesCombined);
            if (!parseResult.isSuccessful()) {
                // Wrap in a dummy class to ensure the syntax is valid for parsing
                String dummyClassWrapper = "class DummyClass {\n" + addedLinesCombined + "\n}";
                parseResult = new JavaParser().parse(dummyClassWrapper);
            }

            if (parseResult.isSuccessful() && parseResult.getResult().isPresent()) {
                CompilationUnit cu = parseResult.getResult().get();
                FieldAddedVisitor visitor = new FieldAddedVisitor();
                visitor.visit(cu, null);
                if (!visitor.getAddedFieldName().isEmpty()) {
                    return visitor.getAddedFieldName();
                }
            }
        }
        return ""; // Return an empty string if no added field is found
    }

    private static class FieldAddedVisitor extends VoidVisitorAdapter<Void> {
        private String addedFieldName = "";

        @Override
        public void visit(FieldDeclaration n, Void arg) {
            super.visit(n, arg);
            // Assuming we're looking for the first added field for simplicity
            if (addedFieldName.isEmpty()) {
                addedFieldName = n.getVariables().get(0).getNameAsString();
            }
        }

        public String getAddedFieldName() {
            return addedFieldName;
        }
    }
}
