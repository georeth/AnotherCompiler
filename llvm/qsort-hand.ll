; vim: ts=2 sw=2
@str = private unnamed_addr constant [13 x i8] c"hello world\0A\00"
@fmt.dn = private unnamed_addr constant [4 x i8] c"%d\0A\00"
@fmt.debug = private unnamed_addr constant [9 x i8] c"%d - %d\0A\00"
@fmt.debug1 = private unnamed_addr constant [11 x i8] c"L %d - %d\0A\00"
@fmt.debug2 = private unnamed_addr constant [11 x i8] c"R %d - %d\0A\00"
@fmt.debug3 = private unnamed_addr constant [11 x i8] c"E %d - %d\0A\00"
@fmt.debug4 = private unnamed_addr constant [11 x i8] c"e %d - %d\0A\00"
@arr = global [30 x i32] zeroinitializer


define void @quicksort(i32* %arr, i32 %from, i32 %to){
  %p.left = alloca i32                ; VAR
  %p.right = alloca i32               ; VAR
  ; left = from + 1
  %left1 = add i32 %from, 1
  store i32 %left1, i32* %p.left
  ; if (left >= to)
  %cond1 = icmp sge i32 %left1, %to
  br i1 %cond1, label %ret, label %cont
cont:
  ; pivot = arr[from]
  %arr.from.ptr = getelementptr i32* %arr, i32 %from
  %pivot = load i32* %arr.from.ptr    ; PIVOT
  ; right = to - 1
  %right1 = sub i32 %to, 1
  store i32 %right1, i32* %p.right
  ; while 
  br label %while.check
while.loop:
  %left2 = load i32* %p.left
  %arr.left2.ptr = getelementptr i32* %arr, i32 %left2
  %arr.left2 = load i32* %arr.left2.ptr
  %cond.if = icmp slt i32 %arr.left2, %pivot
  br i1 %cond.if, label %if.true, label %if.false
if.true:
  ; left = left + 1
  %left3 = load i32* %p.left
  %left3.newval = add i32 %left3, 1
  store i32 %left3.newval, i32* %p.left
  br label %while.check
if.false:
  ; swap arr[left], arr[right]
  ;    calc ptrs
  %left4 = load i32* %p.left
  %arr.left4.ptr = getelementptr i32* %arr, i32 %left4
  %right4 = load i32* %p.right
  %arr.right4.ptr = getelementptr i32* %arr, i32 %right4
  ;    temp = arr[left]
  %temp = load i32* %arr.left4.ptr
  ;    arr[left] = arr[right]
  %arr.right4 = load i32* %arr.right4.ptr
  store i32 %arr.right4, i32* %arr.left4.ptr
  ;    arr[right] = temp
  store i32 %temp, i32* %arr.right4.ptr
  ;    right = right - 1
  %right4.newval = sub i32 %right4, 1
  store i32 %right4.newval, i32 *%p.right
  br label %while.check
while.check:
  %left5 = load i32* %p.left
  %right5 = load i32* %p.right
  %cond = icmp sle i32 %left5, %right5
  br i1 %cond, label %while.loop, label %while.end
while.end:
  %right6 = load i32* %p.right
  %left6 = load i32* %p.left
  %arr.right6.ptr = getelementptr i32* %arr, i32 %right6
  %arr.right6 = load i32* %arr.right6.ptr
  store i32 %arr.right6, i32* %arr.from.ptr
  store i32 %pivot, i32* %arr.right6.ptr

  call void @quicksort(i32* %arr, i32 %from, i32 %right6)
  call void @quicksort(i32* %arr, i32 %left6, i32 %to)
  br label %ret
ret:
  ret void
}

define i32 @main(){
  %i = alloca i32
  ; init the array
  store i32 77726, i32* getelementptr ([30 x i32]* @arr, i32 0, i64 0), align 4
  store i32 68610, i32* getelementptr ([30 x i32]* @arr, i32 0, i64 1), align 4
  store i32 39002, i32* getelementptr ([30 x i32]* @arr, i32 0, i64 2), align 4
  store i32 93549, i32* getelementptr ([30 x i32]* @arr, i32 0, i64 3), align 4
  store i32 92911, i32* getelementptr ([30 x i32]* @arr, i32 0, i64 4), align 4
  store i32 2083, i32* getelementptr ([30 x i32]* @arr, i32 0, i64 5), align 4
  store i32 26349, i32* getelementptr ([30 x i32]* @arr, i32 0, i64 6), align 4
  store i32 42982, i32* getelementptr ([30 x i32]* @arr, i32 0, i64 7), align 4
  store i32 53518, i32* getelementptr ([30 x i32]* @arr, i32 0, i64 8), align 4
  store i32 68650, i32* getelementptr ([30 x i32]* @arr, i32 0, i64 9), align 4
  store i32 52580, i32* getelementptr ([30 x i32]* @arr, i32 0, i64 10), align 4
  store i32 19762, i32* getelementptr ([30 x i32]* @arr, i32 0, i64 11), align 4
  store i32 45137, i32* getelementptr ([30 x i32]* @arr, i32 0, i64 12), align 4
  store i32 83427, i32* getelementptr ([30 x i32]* @arr, i32 0, i64 13), align 4
  store i32 25072, i32* getelementptr ([30 x i32]* @arr, i32 0, i64 14), align 4
  store i32 36143, i32* getelementptr ([30 x i32]* @arr, i32 0, i64 15), align 4
  store i32 97471, i32* getelementptr ([30 x i32]* @arr, i32 0, i64 16), align 4
  store i32 49178, i32* getelementptr ([30 x i32]* @arr, i32 0, i64 17), align 4
  store i32 97011, i32* getelementptr ([30 x i32]* @arr, i32 0, i64 18), align 4
  store i32 28716, i32* getelementptr ([30 x i32]* @arr, i32 0, i64 19), align 4
  store i32 96825, i32* getelementptr ([30 x i32]* @arr, i32 0, i64 20), align 4
  store i32 48507, i32* getelementptr ([30 x i32]* @arr, i32 0, i64 21), align 4
  store i32 79181, i32* getelementptr ([30 x i32]* @arr, i32 0, i64 22), align 4
  store i32 43650, i32* getelementptr ([30 x i32]* @arr, i32 0, i64 23), align 4
  store i32 99288, i32* getelementptr ([30 x i32]* @arr, i32 0, i64 24), align 4
  store i32 6265, i32* getelementptr ([30 x i32]* @arr, i32 0, i64 25), align 4
  store i32 20931, i32* getelementptr ([30 x i32]* @arr, i32 0, i64 26), align 4
  store i32 55334, i32* getelementptr ([30 x i32]* @arr, i32 0, i64 27), align 4
  store i32 67905, i32* getelementptr ([30 x i32]* @arr, i32 0, i64 28), align 4
  store i32 92, i32* getelementptr inbounds ([30 x i32]* @arr, i32 0, i64 29), align 4

  ; call the quicksort
  call void @quicksort(i32* getelementptr ([30 x i32]* @arr, i32 0, i32 0), i32 0, i32 30)

  ; print the array
  store i32 0, i32* %i
  br label %print.check
print.loop:
  %i.val = load i32* %i
  %ptr = getelementptr [30 x i32]* @arr, i32 0, i32 %i.val
  %val = load i32* %ptr
  call i32 (i8*, ...)* @printf(i8* getelementptr ([4 x i8]* @fmt.dn, i32 0, i32 0), i32 %val)

  %i.newval = add i32 %i.val, 1
  store i32 %i.newval, i32* %i
  br label %print.check
print.check:
  %i.val2 = load i32* %i
  %cond = icmp slt i32 %i.val2, 30
  br i1 %cond, label %print.loop, label %print.end
print.end:
  ret i32 0
}

declare i32 @printf(i8*, ...) #1

; vim: ts=2 sw=2 sts=2
