import re

roots = {}
learned = {}
rules = {}
facts = []


def teach(cmd):
    if '-R ' in cmd:
        cmd = cmd.split('-R ')[1]
        var, value = cmd.split(' = ')
        roots[var] = [False, value.replace('"', '').strip(), False]
        roots[var][2] = True
    elif '-L ' in cmd:
        cmd = cmd.split('-L ')[1]
        var, value = cmd.split(' = ')
        learned[var] = [False, value.replace('"', '').strip(), False]

    elif '=' in cmd:
        s = cmd.split(' ')
        var = s[1]
        truth_value = s[3]
        if var in roots:
            if roots[var][2] is True:
                for v in learned:
                    learned[v][0] = False
                    learned[v][2] = False
                    if v in facts:
                        facts.remove(v)
                if truth_value == 'false':
                    if var in facts:
                        facts.remove(var)
            if truth_value == 'false':
                truth_value = False
            else:
                truth_value = True
            roots[var][0] = truth_value
            if truth_value is True:
                facts.append(var)
        else:
            print("Only root variables can be set directly")

    elif '->' in cmd:
        s = cmd.split(' ')
        expr = s[1]
        var = s[3]
        if var in roots:
            print("value after -> must be a Learned Variable")
        else:
            if parse_expression(expr) is not None:
                rules[expr] = var
    else:
        print('Syntax error')


def parse_expression(expr):
    expression = expr
    variables = sorted(re.split('&|\||!|\(|\)', expr), key=len, reverse=True)
    while '' in variables:
        variables.remove('')
    for v in variables:
        if v in roots:
            if roots[v][0] is True:
                expression = expression.replace(v, '$')
            else:
                expression = expression.replace(v, '%')
        elif v in learned:
            if learned[v][0] is True:
                expression = expression.replace(v, '$')
            else:
                expression = expression.replace(v, '%')
        else:
            print('one or more undeclared variables')
            return
    expression = expression.replace('!', ' not ')
    expression = expression.replace('&', ' and ')
    expression = expression.replace('|', ' or ')
    expression = expression.replace('$', 'True')
    expression = expression.replace('%', 'False')
    truth_value = eval(expression)
    return truth_value


def list_all():
    print('Root Variables:')
    for var in roots:
        print('\t%s = "%s"' % (var, roots[var][1]))
    print('\nLearned Variables:')
    for var in learned:
        print('\t%s = "%s"' % (var, learned[var][1]))
    print('\nFacts:')
    for fact in facts:
        print('\t%s' % fact)
    print('\nRules:')
    for rule in rules:
        print('\t%s -> %s' % (rule, rules[rule]))


def learn():
    for expr in rules:
        truth_value = parse_expression(expr)
        var = rules[expr]
        if truth_value is True and learned[var][2] is False:
            learned[var][2] = expr
            learned[var][0] = truth_value
            facts.append(var)
        learn()


def query(expr):
    print(parse_expression(expr))


def why(expr):
    variables = sorted(re.split('&|\||!|\(|\)', expr), key=len, reverse=True)
    while '' in variables:
        variables.remove('')
    result = parse_expression(expr)
    print(result)
    for var in variables:
        if var in roots:
            if roots[var][0] is True:
                print('I KNOW THAT %s' % (roots[var][1]))
            else:
                print('I KNOW IT IS NOT TRUE THAT %s' % (roots[var][1]))
        else:
            rule = learned[var][2]
            if rule is False:
                print('I KNOW IT IS NOT TRUE THAT %s' % (learned[var][1]))
            else:
                args = sorted(re.split('&|\||!|\(|\)', learned[var][2]), key=len, reverse=True)
                while '' in args:
                    args.remove('')
                for arg in args:
                    if arg in roots:
                        statement2 = learned[var][1]
                        if parse_expression(learned[var][2]) is True:
                            print('BECAUSE %s I KNOW THAT %s' % (roots[arg][1], statement2))
                        else:
                            print('BECAUSE It IS NOT TRUE THAT %s I CANNOT PROVE %s' % (roots[arg][1], statement2))
                    else:
                        if eval(learned[var][2]) is True:
                            print('BECAUSE %s I KNOW THAT %s' % (learned[arg][1], statement2))
                        else:
                            print('BECAUSE IT IS NOT TRUE THAT %s I CANNOT PROVE %s' % (learned[arg][1], statement2))
    expression = expr
    expr_lookup = []
    for v in variables:
        if v in roots:
            expression = expression.replace(v, str(len(expr_lookup)))
            expr_lookup.append(roots[v][1])
        else:
            expression = expression.replace(v, str(len(expr_lookup)))
            expr_lookup.append(learned[v][1])
    for e in reversed(range(len(expr_lookup))):
        expression = expression.replace(str(e), expr_lookup[int(e)])
    expression = expression.replace('!', ' NOT ')
    expression = expression.replace('&', ' AND ')
    expression = expression.replace('|', ' OR ')
    if result is True:
        print('THUS I KNOW THAT %s' % expression)
    else:
        print('THUS I CANNOT PROVE THAT %s' % expression)


def read(command):

    if command == 'Learn':
        learn()
    elif command == 'List':
        list_all()
    else:
        s = command.split(' ')
        prefix = s[0]
        if prefix == 'Query':
            query(s[1])
        elif prefix == 'Why':
            why(s[1])
        elif prefix == 'Teach':
            teach(command)
        else:
            print('Invalid Input')
