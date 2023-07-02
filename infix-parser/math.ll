; simple math test

; declare string for printf purposes
@.str = private unnamed_addr constant [3 x i8] c"%f\00", align 1

declare i32 @printf(i8*, ...)

define i32 @main() {
    %x1 = fadd float 4.0, 5.0
    %x2 = fmul float 2.0, %x1
    %x3 = fdiv float %x2, 3.0
    %x4 = fpext float %x3 to double
    %x5 = call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([3 x 
            i8], [3 x i8]* @.str, i64 0, i64 0), double %x4)
    ret i32 0
}