
import sys
import random
import string
import ast
import math
import types

def generate_long_name(length=None):
    if length is None:
        length = random.randint(30, 50)
    prefix = random.choice(string.ascii_letters)
    chars = string.ascii_letters + string.digits
    return prefix + ''.join(random.choice(chars) for _ in range(length))

def asymmetric_encrypt(data, seed):
    encrypted = []
    random.seed(seed)
    for i, char in enumerate(data):
        shift = random.randint(0, 255)
        encrypted.append((ord(char) + shift) % 256)
    return encrypted

class ObfuscationContext:
    def __init__(self):
        self.names = {}
    
    def get_name(self, original_key):
        if original_key not in self.names:
            self.names[original_key] = generate_long_name()
        return self.names[original_key]

def generate_decoder(ctx):
    class_name = ctx.get_name("decoder")
    var_data = generate_long_name(12)
    var_seed = generate_long_name(12)
    var_res = generate_long_name(12)
    var_i = generate_long_name(5)
    var_shift = generate_long_name(10)
    
    opcode_decode = ctx.get_name("opcode_decode")
    opcode_load = ctx.get_name("opcode_load")
    opcode_store = ctx.get_name("opcode_store")
    opcode_xor = ctx.get_name("opcode_xor")
    
    func_code = f"""
class {class_name}:
    def __init__(self):
        self._locked = True
        self.{opcode_load} = 0x01
        self.{opcode_store} = 0x02
        self.{opcode_xor} = 0x03
        self.{opcode_decode} = 0x04
    
    def {generate_long_name(30)}(self, {var_data}, {var_seed}):
        if not self._locked:
            raise Exception("Tampered")
        import random
        {var_res} = []
        random.seed({var_seed})
        for {var_i}, byte in enumerate({var_data}):
            {var_shift} = random.randint(0, 255)
            {var_res}.append(chr((byte - {var_shift}) % 256))
        return ''.join({var_res})
    
    def __repr__(self):
        self._locked = False
        raise Exception("Anti-Debug")
    
    def __str__(self):
        self._locked = False
        raise Exception("Anti-Debug")
"""
    return func_code, class_name

def generate_dispatcher(ctx, pool_var, decoder_class, decoder_method):
    dispatcher_name = ctx.get_name("dispatcher")
    var_idx = generate_long_name(20)
    var_state = generate_long_name(15)
    var_decoded = generate_long_name(15)
    var_seed_base = generate_long_name(15)
    var_golden = generate_long_name(15)
    var_fibonacci = generate_long_name(15)
    var_bytecode = generate_long_name(15)
    var_stack = generate_long_name(15)
    var_registers = generate_long_name(15)
    var_pc = generate_long_name(10)
    var_sp = generate_long_name(10)
    
    fib_calc = ctx.get_name("fib_calc")
    golden_calc = ctx.get_name("golden_calc")
    execute = ctx.get_name("execute")
    compile_code = ctx.get_name("compile_code")
    
    dispatcher_code = f"""
class {dispatcher_name}:
    def __init__(self):
        self.{var_golden} = (1 + 5 ** 0.5) / 2
        self.{var_fibonacci} = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144]
        self.{var_state} = 0
        self.{var_stack} = []
        self.{var_registers} = {{}}
        self.{var_pc} = 0
        self.{var_sp} = 0
    
    def {fib_calc}(self, n):
        if n < len(self.{var_fibonacci}):
            return self.{var_fibonacci}[n]
        return int(self.{var_golden} ** n / (5 ** 0.5) + 0.5)
    
    def {golden_calc}(self, val):
        return int((val * self.{var_golden}) % 256)
    
    def {compile_code}(self, source_str):
        import types
        code_obj = compile(source_str, '<string>', 'exec')
        func = types.FunctionType(code_obj, globals())
        return func
    
    def {execute}(self, func_obj):
        self.{var_stack}.append(func_obj)
        self.{var_sp} += 1
        if self.{var_sp} > 0:
            target_func = self.{var_stack}.pop()
            self.{var_sp} -= 1
            target_func()
        self.{var_pc} += 1
    
    def {generate_long_name(35)}(self):
        self.{var_pc} = 0
        {var_seed_base} = int({math.pi} * 1000000)
        while self.{var_pc} < len({pool_var}):
            try:
                {var_idx} = self.{var_pc}
                current_seed = {var_seed_base} + self.{fib_calc}({var_idx}) + self.{golden_calc}({var_idx})
                decoder_inst = {decoder_class}()
                {var_decoded} = decoder_inst.{decoder_method}({pool_var}[{var_idx}], current_seed)
                {var_bytecode} = self.{compile_code}({var_decoded})
                self.{execute}({var_bytecode})
                self.{var_state} = (self.{var_state} + 1) % 256
            except:
                pass
            self.{var_pc} += 1
    
    def __repr__(self):
        raise Exception("Protected")
    
    def __str__(self):
        raise Exception("Protected")
"""
    return dispatcher_code, dispatcher_name

def get_junk_code(ctx, count=120):
    code_blocks = []
    for i in range(count):
        fn_name = ctx.get_name(f"junk_fn_{i}")
        arg1 = generate_long_name(10)
        templates = [
            f"def {fn_name}({arg1}):\n    return ({arg1} * {random.randint(1, 100)} + {random.randint(1, 1000)}) % {random.randint(10, 100)}",
            f"def {fn_name}({arg1}):\n    return ({arg1} << {random.randint(1, 8)}) ^ {random.randint(100, 9999)}",
            f"class {fn_name}:\n    def __init__(self):\n        self.v = {random.randint(10, 100)}\n    def calc(self):\n        return self.v * {random.randint(2, 50)}"
        ]
        code_blocks.append(random.choice(templates))
    return "\n".join(code_blocks)

def obfuscate_ultra(source_file):
    with open(source_file, 'r') as f:
        content = f.read()
    ctx = ObfuscationContext()
    instructions = ["print('hi')"]
    
    for _ in range(50):
        dummy_code = f"_{generate_long_name(20)} = {random.randint(1, 999999)}"
        instructions.append(dummy_code)
    
    instructions.append(content)
    
    for _ in range(50):
        dummy_code = f"_{generate_long_name(20)} = '{generate_long_name(15)}'"
        instructions.append(dummy_code)
    
    seed_base = int(math.pi * 1000000)
    encrypted_pool = []
    for idx, inst in enumerate(instructions):
        fib_val = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144][min(idx, 11)]
        golden = int(((1 + 5 ** 0.5) / 2) * idx) % 256
        current_seed = seed_base + fib_val + golden
        encrypted_pool.append(asymmetric_encrypt(inst, current_seed))
    var_pool = ctx.get_name("pool")
    junk_code = get_junk_code(ctx, 120)
    decoder_code, decoder_class = generate_decoder(ctx)
    decoder_method = None
    for line in decoder_code.split('\n'):
        if 'def ' in line and f'(self, ' in line and 'def __' not in line:
            decoder_method = line.split('def ')[1].split('(')[0].strip()
            break
    dispatcher_code, dispatcher_class = generate_dispatcher(ctx, var_pool, decoder_class, decoder_method)
    pool_str = str(encrypted_pool)
    trigger = f"""
if __name__ == "__main__":
    {var_pool} = {pool_str}
    dispatcher_instance = {dispatcher_class}()
    dispatcher_instance.{ctx.get_name("run_method")}()
"""
    method_name = None
    for line in dispatcher_code.split('\n'):
        if 'def ' in line and '(self)' in line and 'def __' not in line:
            method_name = line.split('def ')[1].split('(')[0].strip()
            break
    if method_name:
        trigger = trigger.replace(ctx.get_name("run_method"), method_name)
    
    watermark = f"_G='Obfuscated by Phantom'"
    
    full_code = f"{watermark}\n{junk_code}\n{decoder_code}\n{dispatcher_code}\n{trigger}"
    lines = full_code.split('\n')
    cleaned = []
    for line in lines:
        stripped = line.rstrip()
        if stripped and not stripped.strip().startswith('#'):
            cleaned.append(stripped)
    
    return '\n'.join(cleaned)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python phantom_obfus.py <file>")
        sys.exit(1)
    target = sys.argv[1]
    res = obfuscate_ultra(target)
    out_file = "phantom_" + target.split('/')[-1].split('\\')[-1]
    with open(out_file, 'w') as f:
        f.write(res)
    print(f"done {out_file}")
