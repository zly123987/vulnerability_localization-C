package Structure;

import com.github.javaparser.ast.*;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;

public class Clazz {
    String name;
    String body;
    String comment;
    boolean isInterface = false;
    HashSet<String> varDef = new HashSet<>();
    HashSet<String> varRef = new HashSet<>();

    List<Method> methods = new ArrayList<Method>();
    ArrayList<String> modifiers = new ArrayList<>();

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

    public void addMethod(Method m){
        this.methods.add(m);
    }

    public ArrayList<String> getModifiers() {
        return modifiers;
    }

    public void setModifiers(NodeList<Modifier> modifiers) {
        for(Modifier mod: modifiers){
            this.modifiers.add(mod.toString().strip());
        }
    }

    public boolean isInterface() {
        return isInterface;
    }

    public void setInterface(boolean anInterface) {
        isInterface = anInterface;
    }


    public HashSet<String> getVarDef() {
        return varDef;
    }

    public HashSet<String> getVarRef() {
        return varRef;
    }
}
