# Tables description



## Propósito



Este documento resume las tablas principales contenidas en la base sintética y su función dentro del caso de estudio.



## Tablas principales



### DIM\_PROSPECT

Contiene atributos descriptivos del prospecto. Su granularidad es un registro por prospecto.



### DIM\_CHANNEL

Catálogo de canales de adquisición digital.



### DIM\_CAMPAIGN

Catálogo de campañas asociadas a canales, plataformas y objetivos de marketing.



### DIM\_DEVICE

Describe el tipo de dispositivo, sistema operativo y entorno de navegación utilizado.



### DIM\_FUNNEL\_STAGE

Catálogo de etapas del funnel utilizadas para trazabilidad analítica.



### FACT\_JOURNEY

Representa el recorrido integral del usuario a lo largo del funnel.



### FACT\_SESSION

Registra sesiones digitales asociadas al journey del prospecto.



### FACT\_INTERACTION\_EVENT

Almacena eventos de interacción dentro de sesiones y journeys.


### FACT\_LEAD

Registra la creación y calidad de los leads generados.



### FACT\_REGISTRATION

Modela el proceso de inicio, avance, finalización o abandono del registro.



### FACT\_ACTIVATION

Representa la activación posterior al registro y señales de adopción inicial.



### FACT\_JOURNEY\_STAGE

Traza el avance del prospecto por etapas del funnel.

