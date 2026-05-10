## Esquema MySQL

Tabla `accesos` en la base `rfid_registro`:

| nombre | tipo | constraint |
|--------|------|------------|
| id | INT | PRIMARY KEY |
| nombre | VARCHAR | NOT NULL |
| acceso_concedido | BOOLEAN | NOT NULL |
| fecha | TIMESTAMP | |

```sql
CREATE TABLE accesos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uuid VARCHAR(20) NOT NULL,
    nombre VARCHAR(100),
    acceso_concedido BOOLEAN NOT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```
