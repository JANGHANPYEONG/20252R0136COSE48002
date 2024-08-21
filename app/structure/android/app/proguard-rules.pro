# Keep the EscPosEmul class and its members
-keep class com.bixolon.commonlib.emul.EscPosEmul {
    public *;
    protected *;
    private *;
}

# Keep the entire package if it contains native methods
-keep class com.bixolon.** { *; }

# Keep all classes used in native code
-keepclasseswithmembernames class * {
    native <methods>;
}

# Keep all native method names and signatures
-keepclasseswithmembernames class * {
    native <methods>;
}
