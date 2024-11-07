#include <stdio.h>
#include <math.h>

int task_1(){
    int n; // количество чисел
    printf("Сколько чисел вы хотите ввести? ");
    scanf("%d", &n); // ввод количества чисел

    if (n <= 0) {
        printf("Количество чисел должно быть положительным.\n");
        return 1;
    }

    double sum = 0; // сумма чисел
    double number;  // временная переменная для ввода числа

    // цикл для ввода чисел и вычисления суммы
    for (int i = 0; i < n; i++) {
        printf("Введите число %d: ", i + 1);
        scanf("%lf", &number); // ввод числа
        sum += number;         // добавление числа к сумме
    }

    double average = sum / n; // вычисление среднего значения

    printf("Среднее значение введенных чисел: %.2lf\n", average);
    return 0;
}
int task_2(){
    char input[12]; // Массив для ввода строки (10 символов + пробелы и '\0')
    
    // Запрос на ввод пятизначного числа с пробелами
    printf("Введите пятизначное число с пробелами (например, 1 2 3 4 5): ");
    fgets(input, sizeof(input), stdin); // Считывание строки с пробелами

    printf("Число без пробелов: ");
    
    // Цикл для вывода цифр без пробелов
    for (int i = 0; input[i] != '\0'; i++) {
        if (input[i] != ' ' && input[i] != '\n') { // Проверка на пробелы и символ новой строки
            printf("%c", input[i]); // Вывод символа
        }
    }

    printf("\n");
    return 0;
}
int task_4(){
    int A, B;

    // Ввод двух чисел A и B
    printf("Введите два числа A и B: ");
    scanf("%d %d", &A, &B);

    // Проверка, какое из чисел меньше, и вывод чисел в порядке возрастания
    if (A > B) {
        // Если A больше B, то выводим числа от B до A
        for (int i = B; i <= A; i++) {
            printf("%d ", i);
        }
    } else {
        // Если B больше или равно A, то выводим числа от A до B
        for (int i = A; i <= B; i++) {
            printf("%d ", i);
        }
    }

    printf("\n");
    return 0;
}
int task_5(){
    int n;
    unsigned long long factorial = 1; // Используем unsigned long long для больших чисел

    // Ввод числа
    printf("Введите число для вычисления факториала: ");
    scanf("%d", &n);

    // Проверка на неотрицательное число
    if (n < 0) {
        printf("Факториал отрицательных чисел не существует.\n");
    } else {
        // Вычисление факториала с помощью цикла
        for (int i = 1; i <= n; i++) {
            factorial *= i;
        }
        printf("Факториал числа %d = %llu\n", n, factorial);
    }

    return 0;
}


int task_6() {
    double radius, depth, volume;

    // Ввод радиуса и глубины бассейна
    printf("Введите радиус бассейна (м): ");
    scanf("%lf", &radius);

    printf("Введите глубину бассейна (м): ");
    scanf("%lf", &depth);

    // Вычисление объема бассейна
    volume = M_PI * radius * radius * depth;

    // Вывод объема бассейна
    printf("Объем бассейна: %.2f м3\n", volume);

    // Проверка объема и вывод сообщения
    if (volume > 300) {
        printf("Это большой бассейн.\n");
    }

    return 0;
}

int main() {
    int result = task_1(); 
    int rs = task_2();
    task_3(); 
    // task_4();
    // task_5();
    return 0;
}
