package RCL.structures;

public class FieldDeclr {
    private String name;
    private String type;
    private String declardClass;
    private boolean isStatic;


    public FieldDeclr(String name, String type, String declardClass, boolean isStatic) {
        this.name = name;
        this.type = type;
        this.declardClass = declardClass;
        this.isStatic = isStatic;

    }

    public String getName() {
        return name;
    }

    public String getType() {
        return type;
    }

    public String getDeclardClass() {
        return declardClass;
    }

    public boolean isStatic() {
        return isStatic;
    }

    public String toString() {
        return name;
    }
}
