    if n % 2 == 0 then
      // yes 表示布尔真值
      return yes;
    end if
    // no 表示布尔假
    return no;

    if m == 0 then
      return n + 1;
    elif m > 0 and n == 0 then
      return ackerman(m - 1, 1);
    else
      return ackerman(m - 1, ackerman(m, n - 1));
    end if

    i := 0;
    // 如果 i < 10 成立则进入循环体
    while i < 10 do
      j := 0;
      // 无论何种条件，进入循环体
      repeat
        g[i][j] := i * j;
      // 如果 j >= 10 成立则退出循环，否则回到循环开始
      until j >= 10;
      i := i + 1;
    // 此时回到循环的条件判断处
    end while
    // 遍历 g 中的每个元素
    foreach l in g do
      foreach i in l do
        print i;
      end foreach
    end foreach

      t := x + v;
      v := x;
      return t;

      v := v + x;
      return v;

  print p.f(5);
  print q.f(4);
  p.v := 3;
  print p.f(3);
  multy();
  print ackerman(3, 4);
  if isodd(3) then
    print 3;
  end if
