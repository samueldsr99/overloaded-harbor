# Overloaded Harbor

## Proyecto de Simulación

* `Samuel David Suárez Rodríguez C-412`

## Ejecutar

Para ejecutar con los valores por defecto

```bash
python main.py
```

Puede encontrar ayuda sobre los parámetros que puede modificar de la simulación
ejecutando la ayuda

```bash
python main.py -h
```

## Orden del problema

En un puerto de supertanqueros que cuenta con 3 muelles y un remolcador
para la descarga de estos barcos de manera simultánea se desea conocer el tiempo
promedio de espera de los barcos para ser cargados en el puerto.

El puerto cuenta con un bote remolcador disponible para asistir a los tanqueros. Los tanqueros de cualquier tamaño necesitan de un remolcador para
aproximarse al muelle desde el puerto y para dejar el muelle de vuelta al puerto.

El tiempo de intervalo de arribo de cada barco distribuye mediante una función exponencial
con $\lambda = 8$ horas. Existen tres tamaños distintos de tanqueros:
pequeño, mediano y grande, la probabilidad correspondiente al tamaño de cada
tanquero se describe en la tabla siguiente. El tiempo de carga de cada tanquero
depende de su tamaño y los parámetros de distribución normal que lo representa
también se describen en la tabla siguiente.

| Tamaño  | Probabilidad de Arribo | Tiempo de Carga          |
| ---     | ---                    | ---                      |
| Pequeño | 0.25                   | $\mu = 9, \sigma^2 = 1$  |
| Mediano | 0.25                   | $\mu = 12, \sigma^2 = 2$ |
| Grande  | 0.5                    | $\mu = 18, \sigma^2 = 3$ |

De manera general, cuando un tanquero llega al puerto, espera en una cola
(virtual) hasta que exista un muelle vacío y que un remolcador esté disponible
para atenderle. Cuando el remolcador está disponible lo asiste para que pueda
comenzar su carga, este proceso demora un tiempo que distribuye exponencial
con $\lambda = 2$ horas. El proceso de carga comienza inmediatamente después de que
el barco llega al muelle. Una vez terminado este proceso es necesaria la asistencia
del remolcador (esperando hasta que esté disponible) para llevarlo de vuelta al
puerto, el tiempo de esta operación distribuye de manera exponencial con $\lambda = 1$
hora. El traslado entre el puerto y un muelle por el remolcador sin tanquero
distribuye exponencial con $\lambda = 15$ minutos.

Cuando el remolcador termina la operación de aproximar un tanquero al
muelle, entonces lleva al puerto al primer barco que esperaba por salir, en caso de
que no exista barco por salir y algún muelle esté vacío, entonces el remolcador se
dirige hacia el puerto para llevar al primer barco en espera hacia el muelle vacío;
en caso de que no espere ningún barco, entonces el remolcador esperará por algún barco en un muelle para llevarlo al puerto. Cuando el remolcador termina
la operación de llevar algún barco al puerto, este inmediatamente lleva al primer
barco esperando hacia el muelle vacío. En caso de que no haya barcos en los
muelles, ni barcos en espera para ir al muelle, entonces el remolcador se queda
en el puerto esperando por algún barco para llevar a un muelle.

Simule completamente el funcionamiento del puerto. Determine el tiempo
promedio de espera en los muelles.

## Modelo utilizado

Para resolver el problema anteriormente descrito se utilizó un modelo en serie,
compuesto por el remolcador y los muelles, estos muelles a su vez componen un
modelo de servidores en paralelo, en donde cada servidor representa un muelle, y los
clientes son los usuarios que llegan al puerto.

## Principales ideas

La idea principal se basa en ejecutar los eventos ordenados en paralelo para cada
muelle y llevar un seguimiento del estado del remolcador para saber si un barco
debe esperar o puede ser atendido, estos cambios de estado se encargan de
permitir que el flujo continue o se detenga en dependencia de las transiciones
de estado.

Para simular el hilo de cada servidor(muelle) establecimos un flujo cada vez
que un barco llega a este, determinado como:

- Llegar
- Encolar el barco
- Trasladarse hasta el muelle
- Cargar
- Confirmar terminación con el remolcador
- Ida del puerto

Una vez que un proceso de un hilo es terminado, añade un nuevo evento con el
proceso siguiente en la cola de eventos.

### Variables

- De tiempo
  - `time`: Línea de tiempo de la simulación.
  - `arrivals`: Momento de llegada de cada barco al puerto.
  - `departures`: Momento de salida de cada barco del puerto.
  - `dock_arrivals`: Momento de llegada de cada barco al muelle.
  - `dock_departures`: Momento de salida de cada barco del muelle.

- De estado
  - `tugboat_state`: Estado de el remolcador (0: en un muelle, 1: en el puerto).
  - `tugboat_blocked`: True si el remolcador está ocupado, False en otro caso.
  - `size`: Tamaño de cada barco (0: pequeño, 1: mediano, 2: grande).

- Contadoras
  - `n`: Cantidad de barcos inicial.
  - `s_counter`: Cantidad de barcos que llegan al puerto en el instante de tiempo actual.
  - `docks`: Cantidad de muelles libres en el instante de tiempo actual.

## Resultados

Los siguientes resultados son basados en el valor obtenido para la cantidad de
barcos mencionada a continuación luego 5000 repeticiones y 3 muelles, el tiempo medio se
encuentra dado en horas.

| Barcos  | Tiempo medio de espera en el muelle | Tiempo medio de espera en el puerto |
| ---     | ---                                 | ---                                 |
| 5       | 15.63                               | 16.66                               |
| 10      | 15.63                               | 37.13                               |
| 20      | 15.63                               | 64.82                               |
| 50      | 15.63                               | 148.70                              |

Como podemos observar, el incremento de la cantidad de barcos aumenta grandemente
el tiempo promedio de estancia de los barcos en el puerto, esto se
debe a que el único remolcador estará indisponible la mayor cantidad de tiempo
por lo que cuando los muelles están llenos, la cola de los barcos en el puerto
debe esperar a que alguno termine, mientras más barcos existan en esta cola, más
tiempo deberán esperar los últimos.

Por otro lado, el tiempo que permanece cada barco en el muelle no varía grandemente
al aumentar la cantidad de barcos, ya que si contamos el tiempo desde que un barco
llega al muelle, este comenzará a descargar, y para volver, como mucho debe esperar que el
remolcador acabe con los barcos en los muelles restantes o que vuelva del puerto. Otra manera de verlo,
es considerar que una vez que un barco llega a un muelle, este tiene más prioridad
que los que se encuentran en el puerto, por lo que se encontraría en una nueva
cola compuesta por los barcos en el muelle.

Para comprobar que esto es cierto, repetimos el experimento pero esta vez dejamos
fija la cantidad de barcos a ser atendidos, siendo 50 barcos, y observamos los
resultados para distintas cantidades de muelles.

| Muelles | Tiempo medio de espera en el muelle | Tiempo medio de espera en el puerto |
| ---     | ---                                 | ---                                 |
| 3       | 15.63                               | 148.27                               |
| 5       | 15.91                               | 93.46                               |
| 10      | 17.31                               | 55.75                               |
| 20      | 24.38                               | 46.37                              |

Esta vez aumenta el tiempo media de espera en el muelle, debido a lo que explicamos
anteriormente, la "cola" de barcos en los muelles es mayor, y solo hay un
remolcador para atender estos barcos.

Lo otro que observamos es que el tiempo medio de espera en el puerto es menor,
y tiene sentido porque mientras más muelles tenemos, más cantidad de barcos
pueden cargar al mismo tiempo, por lo que es
factible que existan más muelles en el puerto para optimizar el tiempo total.
