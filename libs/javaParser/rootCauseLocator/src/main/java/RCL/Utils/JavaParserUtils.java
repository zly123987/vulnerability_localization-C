package RCL.Utils;

import com.github.javaparser.JavaParser;
import com.github.javaparser.ParseResult;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.expr.MethodCallExpr;
import com.github.javaparser.ast.expr.ObjectCreationExpr;
import com.github.javaparser.ast.visitor.VoidVisitorAdapter;

import java.util.*;

public class JavaParserUtils {
    static List<String> blackList = Arrays.asList("toString", "equals", "hashCode", "getClass", "clone", "notify", "notifyAll", "wait", "length", "charAt", "substring", "indexOf", "toLowerCase", "toUpperCase", "trim", "replace", "split", "abs", "max", "min", "sqrt", "pow", "round", "currentTimeMillis", "nanoTime", "arraycopy", "exit", "gc", "add", "remove", "clear", "size", "isEmpty", "contains", "iterator", "get", "set", "listIterator", "indexOf", "subList", "put", "get", "remove", "keySet", "values", "entrySet", "createNewFile", "delete", "exists", "getAbsolutePath", "isDirectory", "isFile", "list", "read", "write", "close", "read", "write", "flush", "openStream", "getContent", "getProtocol", "getHost", "getPath", "connect", "getInputStream", "getContentLength", "getContentType", "append");
    public static List<String> getBlackList() {
        return blackList;
    }

    public static Map<String, List<String>> extractInvocationsAndInitializations(List<String> lines) {
        Map<String, List<String>> invocationsAndInitializations = new HashMap<>();
        JavaParser parser = new JavaParser();

        lines.forEach(line -> {
            // Wrap each line to form a valid Java structure

            String wrappedCode = "class Dummy {" + line + " }";
            ParseResult<CompilationUnit> result = new JavaParser().parse(wrappedCode);
            if (!result.isSuccessful()) {
                wrappedCode = "class Dummy { void dummyMethod() { " + line + " } }";
                result = parser.parse(wrappedCode);
            }


            result.ifSuccessful(cu -> {
                cu.accept(new VoidVisitorAdapter<Void>() {
                    @Override
                    public void visit(MethodCallExpr mce, Void arg) {
                        super.visit(mce, arg);
                        List<String> argsList = new ArrayList<>();
                        mce.getArguments().forEach(argument -> argsList.add(argument.toString()));
                        // Use the method name and arguments as key-value pairs
                        invocationsAndInitializations.merge(mce.getNameAsString(), argsList, (oldList, newList) -> {
                            oldList.addAll(newList);
                            return oldList;
                        });
                    }

                    @Override
                    public void visit(ObjectCreationExpr oce, Void arg) {
                        super.visit(oce, arg);
                        List<String> argsList = new ArrayList<>();
                        oce.getArguments().forEach(argument -> argsList.add(argument.toString()));
                        // Prefix with "new " to indicate class initialization
                        String key =  oce.getType().asString();
                        invocationsAndInitializations.merge(key, argsList, (oldList, newList) -> {
                            oldList.addAll(newList);
                            return oldList;
                        });
                    }
                }, null);
            });
        });
        if (invocationsAndInitializations.size()==0){
            String wrappedCode = "class Dummy {" + String.join("\n", lines) + " }";
            ParseResult<CompilationUnit> result = new JavaParser().parse(wrappedCode);
            if (!result.isSuccessful()) {
                wrappedCode = "class Dummy { void dummyMethod() { " + String.join("\n", lines) + " } }";
                result = parser.parse(wrappedCode);
            }


            result.ifSuccessful(cu -> {
                cu.accept(new VoidVisitorAdapter<Void>() {
                    @Override
                    public void visit(MethodCallExpr mce, Void arg) {
                        super.visit(mce, arg);
                        List<String> argsList = new ArrayList<>();
                        mce.getArguments().forEach(argument -> argsList.add(argument.toString()));
                        // Use the method name and arguments as key-value pairs
                        invocationsAndInitializations.merge(mce.getNameAsString(), argsList, (oldList, newList) -> {
                            oldList.addAll(newList);
                            return oldList;
                        });
                    }

                    @Override
                    public void visit(ObjectCreationExpr oce, Void arg) {
                        super.visit(oce, arg);
                        List<String> argsList = new ArrayList<>();
                        oce.getArguments().forEach(argument -> argsList.add(argument.toString()));
                        // Prefix with "new " to indicate class initialization
                        String key =  oce.getType().asString();
                        invocationsAndInitializations.merge(key, argsList, (oldList, newList) -> {
                            oldList.addAll(newList);
                            return oldList;
                        });
                    }
                }, null);
            });
        }
        return invocationsAndInitializations;
    }
}
