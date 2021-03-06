
# schepy
编译原理课设, 很简单的类似scheme解释器

当然编译原理和scheme都是初入门， 理解很浅， 例如并不会写尾递归优化


词法分析支持正规文法和简单的正则表达式，语法分析使用LR1分析



## Installation
`git clone https://github.com/ShengRang/schepy`

## Usage
>python main.py

当然也支持pypy, 更快速:
>pypy main.py


你也可以通过修改语法/词法(regular_lex.txt/regex_lex.txt)， 以及解释器的行为， 让解释器具有你想要的特性!

文法的范例参考 grammar.txt， 支持#和'''两种注释(和 Python 差不多)
无需指定终结符/非终结符， 分析程序自动判断

lexer 和 parser 的使用参考main.py， 大致都为先读入文法， 再编译， 后使用
lexer 可以在 `compile` 时指定解析类型为正规文法(`grammar_type="regular"`)或正则表达式(`grammar_type="regex"`)
parser 在 `parse` 时传入 `handler` 控制产生 LR 移进和规约动作时的行为

解释器部分只使用了**分析树**进行代码执行。

一些例子：
```scheme
486                             ; 表达式
(+ 137 349)                     ; 组合式
(+ (* 3 5) (- 10 6))            ; 组合式
(define size 2)                 ; 定义, 将2与size相关联
## (define (square x) (* x x))     ; 复合过程   (define (<name> <formal parameters>) <body>)
(square 21)                     ; 使用过程
(define (sum-of-squares x y)    ; 复合过程
    (+ (square x) (square y)))

(define (f a)                   ; 复合过程
    (sum-of-squares (+ a 1) (* a 2)))

(f 5)                           ; 136
(define (abs x)
    (cond ((> x 0) x)           ; 条件表达式
          ((= x 0) 0)
          ((< x 0) (- x))))

(if (> x 0) (define y x) 2)     ; if表达式 (if test-expr then-expr else-expr) (这个还是用函数实现比较好)
(lambda (x) (+ x 5))            ; lambda表达式 (lambda kw-formals body ...+)

; 延迟求值
(+ (* 3 5) (- 10 6))
(define size 2)
(define x 3)
(if (> x 0) (define y x) 2)
(define a (foo b))
(define foo (lambda (x) (* x x)))
(define b 12)
a


; 实现filter
(define (filter fun s) (define first (car s))
  (if (= (length s) 1)
    (if (fun first) [first] [] )
    (if (fun first) (append [first]  (filter fun (cdr s))) (filter fun (cdr s)))
  )
)


; 快排
(define quick-sort
  (lambda (s)
    (if (< (length s) 2)
      s
      (append
        (quick-sort (filter (lambda (x) (< x (car s))) s ))
        (filter (lambda (x) (= x (car s))) s)
        (quick-sort (filter (lambda (x) (> x (car s))) s ))
      )
    )
  )
)

(quick-sort [-6 -10 3 1 12 -5])

; [-10, -6, -5, 1, 3, 12]
```
