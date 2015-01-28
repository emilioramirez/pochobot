# pochobot
A Willie's module for manage the lunches of Machinalis

![POCHO](http://i.imgur.com/mRcHiPP.jpg)

## Available commnads

    .lunch_create <menu descrition>
    .lunch_publish
    .lunch_cancel
    .lunch_add <nickname>
    .lunch_done <total_price>
    .lunch_detail
 
## Commands detail
    
#### Crear un almuerzo
    .lunch_create milanesas con papas
Con el comando de arriba una persona puede crear un almuerzo, ese almuerzo va quedar activo hasta que el mismo usuario que lo creo, lo cancele. Un usuario puede tener UN solo almuerzo activo a la vez, esto quiere decir que si quiere crear otro mientras tiene uno activo, tiene que cancelar el viejo.


#### Ver el detalle del almuerzo
    .lunch_detail
Si queremos ver el detalle del almuerzo, como por ejemplo cuantos comenzales se anotaron.


#### Cancelar un almuerzo
    .lunch_cancel
Si por alguna razón queremos cancelar el almuerzo que creamos.


#### Publicar el almuerzo en el canal
    .lunch_publish
Cuando creamos el almuerzo y ya estamos conformes con el nombre, con este comando lo publicamos en el canal para que la gente se pueda sumar al almuerzo que uno crea.


#### Sumarse a un almuerzo que alguien creo
    .lunch_add <nickname>
Si nos queremos sumar a algun almuerzo que alguien creo solo tenemos que ejecutar este comando pasando el nick de quien creo el almuerzo


#### Publicar el precio por pera del almuerzo
    .lunch_done <costo total del almuerzo>
Cuando queremos publicar el precio por pera del almuerzo, a este comando hay que pasarle el costo total del almuerzo y el bot se va a encargar de sacarlos calculos teniendo en cuenta las personas que se sumaron y publicar el resultado en el canal.
