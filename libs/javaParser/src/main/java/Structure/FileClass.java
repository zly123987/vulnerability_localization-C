package Structure;

import java.util.ArrayList;
import java.util.List;

public class FileClass {
    String name;
    String body;
    String comment;
    List<Clazz> classes = new ArrayList<>();

    public FileClass(){

    }
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

    public void addClass(Clazz c){
        this.classes.add(c);
    }
}
