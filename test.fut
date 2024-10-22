entry f0 : i64 = 1337

entry f1 (x: i64) : i64 = x + 1

type r = {a:i64, b:bool}
entry const_record : r = {a=42,b=true}

entry failing (x: i64) : i64 = assert false (x + 1)

entry ensure_i32_arr (x: []i32) = x
