package Structure;

import java.util.HashSet;

public class Method {
    String name;
    String body;
    String comment;
    HashSet<String> varDef = new HashSet<>();
    HashSet<String> varRef = new HashSet<>();

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getBody() {
        return body;
    }

    public void setBody(String body) {
        this.body = body;
    }

    public String getComment() {
        return comment;
    }

    public void setComment(String comment) {
        this.comment = comment;
    }

    public HashSet<String> getVarDef() {
        return varDef;
    }

    public HashSet<String> getVarRef() {
        return varRef;
    }
}
