package RCL.structures;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public class PatchDiff {
    String old_file_path;
    String new_file_path;
    List<Diff> diffPairs = new ArrayList<>();

    public PatchDiff(List<DiffChange> changes){
        for (DiffChange change : changes) {
            old_file_path = change.old_file_path;
            new_file_path = change.new_file_path;
            for (Map<String, Object> diff : change.diffs) {
                diffPairs.add(new Diff((List<String>) diff.get("added_lines"), (List<String>) diff.get("removed_lines"), (List<String>) diff.get("context_lines")));
            }
        }
    }
    public static class DiffChange {
        String old_file_path;
        String new_file_path;
        List<Map<String, Object>> diffs;

    }
    public static class Diff {
        List<String> addedLines;
        List<String> removedLines;
        List<String> contextLines;

        public Diff(List<String> addedLines, List<String> removedLines, List<String> context){
            this.addedLines = addedLines;
            this.removedLines = removedLines;
            this.contextLines = context;
        }

        public List<String> getAddedLines() {
            return addedLines;
        }

        public List<String> getRemovedLines() {
            return removedLines;
        }

        public List<String> getContextLines() {
            return contextLines;
        }

    }

    public List<Diff> getDiffs() {
        return diffPairs;
    }

    public String getNew_file_path(){
        return new_file_path;
    }
}
