create database if not exists tp_final_ids;

use tp_final_ids;

create table cursos (
    id int not null auto_increment primary key,
    nombre varchar(100),
    cuatrimestre varchar(20),
    anio int not null,
    modificacion varchar(255)
);

create table clase_presencial
(
    id       int auto_increment primary key,
    curso_id int not null,
    fecha    timestamp,
    foreign key (curso_id) references cursos(id)
);

create table alumnos (
    id int not null auto_increment primary key,
    padron int not null,
    nombre varchar(100),
    apellido varchar(100),
    email varchar(100),
    abandono boolean default false,
    estado boolean default true
);

create table alumnos_curso (
    alumnos_id int not null,
    curso_id int not null,

    primary key (alumnos_id, curso_id),

    foreign key (alumnos_id)
        references alumnos(id),
    foreign key (curso_id)
        references cursos(id)
);

create table profesores (
    id int not null auto_increment primary key,
    nombre varchar(100),
    apellido varchar(100),
    email varchar(100),
    password varchar(255)
);

create table tipos_evaluacion (
    id int not null auto_increment primary key,
    nombre varchar(100)
);

create table evaluaciones (
    id int not null auto_increment primary key,
    titulo varchar(200),
    fecha date,
    tipo_id int not null,
    curso_id int not null,

    foreign key (tipo_id)
        references tipos_evaluacion(id),

    foreign key (curso_id)
        references cursos(id)
);

create table notas (
    id int  not null  auto_increment primary key,
    alumno_id int not null ,
    evaluacion_id int not null ,
    nota_alumno decimal(10),

    foreign key (alumno_id)
        references alumnos(id),
    foreign key (evaluacion_id)
        references evaluaciones(id)
);

create table equipos(
    id      int not null auto_increment primary key,
    nombre         varchar(100),
    descripcion    varchar(255),
    curso_id       int not null,
    fecha_creacion timestamp default current_timestamp,

    foreign key (curso_id)
        references cursos(id)
);

create table equipo_alumnos (
    equipo_id int not null ,
    alumno_id int not null ,

    primary key (equipo_id, alumno_id),

    foreign key (equipo_id)
        references equipos(id),
    foreign key (alumno_id)
        references alumnos(id)
);

create table asistencias (
    id int not null auto_increment primary key,
    alumno_id int not null ,
    curso_id int not null ,
    fecha date,
    presente boolean,
    codigo_qr varchar(100),

    foreign key (alumno_id)
        references alumnos(id),
     foreign key (curso_id)
        references cursos(id)
);

create table login (
    id int not null auto_increment primary key,
    profesor_id int not null ,
    fecha timestamp default current_timestamp,

    foreign key (profesor_id)
        references profesores(id)
);