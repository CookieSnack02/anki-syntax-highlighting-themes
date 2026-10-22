# -*- coding: utf-8 -*-

"""Code samples for the theme preview (no Anki imports)"""

SAMPLES = {
    "python": '''# Fibonacci com memoização
from functools import lru_cache

@lru_cache(maxsize=None)
def fib(n: int) -> int:
    """Retorna o n-ésimo número de Fibonacci."""
    return n if n < 2 else fib(n - 1) + fib(n - 2)

print([fib(i) for i in range(10)])  # {{c1::cloze}}
''',
    "javascript": """// Debounce: atrasa a execução de fn
export function debounce(fn, ms = 300) {
  let timer = null;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn.apply(this, args), ms);
  };
}
console.log(`pronto: ${typeof debounce}`);
""",
    "java": """public class Main {
    // Soma os elementos de um array
    public static int soma(int[] valores) {
        int total = 0;
        for (int v : valores) total += v;
        return total;
    }

    public static void main(String[] args) {
        System.out.println("Total: " + soma(new int[]{1, 2, 3}));
    }
}
""",
    "c": """#include <stdio.h>

/* Troca dois inteiros */
void swap(int *a, int *b) {
    int tmp = *a;
    *a = *b;
    *b = tmp;
}

int main(void) {
    int x = 1, y = 2;
    swap(&x, &y);
    printf("x=%d y=%d\\n", x, y);
    return 0;
}
""",
    "sql": """-- Alunos com média acima de 7
SELECT a.nome, AVG(n.valor) AS media
FROM aluno a
JOIN nota n ON n.id_aluno = a.id
WHERE n.ano = 2026
GROUP BY a.nome
HAVING AVG(n.valor) > 7.0
ORDER BY media DESC;
""",
}
SAMPLES["cpp"] = SAMPLES["c"]
SAMPLES["typescript"] = SAMPLES["javascript"]
