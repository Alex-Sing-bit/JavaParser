import os
import sys

from compiler_demo import program


def main() -> None:
    prog1 = '''
        int input_int(string name) {
            if (name != "") {
                print("Введите " + name + ": ");
            }
            return to_int(read());
        }
        void input_float(string name) {
            if (name != "") {
                print("Введите " + name + ": ");
            }
        }
        
        
        int g, g2 = g, g4 = 90;

        int a = input_int("a");
        float b = input_float("b"), c = input_float("c");  /* comment 1
        int d = input_int("d");
        */
        for (int i = 0, j = 8; ((i <= 5)) && g; i = i + 1, print(5))
            for(; a < b;)
                if (a > 7 + b) {
                    c = a + b * (2 - 1) + 0;  // comment 2
                    string bb = "98\tура";
                }
                else if (a)
                    print((c + 1) + " " + 89.89);
        for(bool i = true;;);

        int z;
        z=0;
    '''
    prog2 = 'int f1(int p1, float p2) { string a = p1 + p2; int x; return 1;}'''
    prog3 = 'for (;;);'
    prog4 = '''
            int input_int(string name) {
                if (name != "") {
                    print("Введите " + name + ": ");
                }
                return to_int(read());

                // bool a() { }
            }
            int input_int2(string name, int a, int name2) {
                if (name != "") {
                    print("Введите " + name + ": ");
                }
                return "";
            }
        '''
    prog5 = ''' 
    int input_int(string name) {
        if (name != "") {
            name += 1;
            name += 'c';
        }
        return 2;
    }

    
    float n = input_int("nnn");
    n += 1;
    '''
    prog6 = ''' 
        String input_int(boolean name) {
            if (name) {
            int w = 1;
            }
            return 'l';
        }
    
         
        '''
    prog7 = ''' 
            int input_int(string name) {
                if (name != "") {
                    name += 1;
                    name += 'c';
                }
                return 2;
            }

            int n = input_int(12, 122);

            '''
    prog8 = ''' 
            n += 1;
            '''
    prog9 = ''' 
            char c = 'f';
            c += "ddd";
                '''
    prog10 = ''' 
                Gggg r = 1;
                r += 1;
                '''
    prog11 = ''' 
                 int j = 1;
              for (int i = 0; i < 10; i = i + 1) {
                  j = 0;
              }
                    '''

    program.execute(prog11)


if __name__ == "__main__":
    main()
