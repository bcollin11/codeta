/*
    Creates the code_ta database
    Only for development and testing, should never be run in
    production

*/

create table if not exists Users (
    user_id bigserial primary key,
    email varchar(100) not null,
    username varchar(100) not null,
    password char(75) not null,
    first_name varchar(100),
    last_name varchar(100)
);

create table if not exists Instructor (
    instructor_id integer,
    contact_email varchar(100),

    foreign key (instructor_id) references Users (user_id) on delete cascade
);

create table if not exists Student (
    student_id integer,

    foreign key (student_id) references Users (user_id) on delete cascade
);

create table if not exists Course (
    course_id bigserial primary key,
    title varchar(100) not null,
    identifier varchar(20),
    section varchar(10),
    description text

);

create table if not exists InstructorTeachesCourse (
    instructor_teaches_course bigserial primary key,
    user_id integer not null,
    course_id integer not null,

    foreign key (user_id) references Users (user_id) on delete cascade,
    foreign key (course_id) references Course (course_id) on delete cascade
);

create table if not exists StudentEnrollsCourse (
    student_enroll_course bigserial primary key,
    user_id integer not null,
    course_id integer not null,

    foreign key (user_id) references Users (user_id) on delete cascade,
    foreign key (course_id) references Course (course_id) on delete cascade

);

create table if not exists Assignment (
    assignment_id bigserial primary key,
    title varchar(100),
    description text,
    due_date timestamp,
    points_possible integer,
    course_id integer,

    foreign key (course_id) references Course (course_id) on delete cascade
);

create table if not exists UserFile (
    user_file_id bigserial primary key,
    assignment_id integer,
    symlink text not null,

    foreign key (assignment_id) references Assignment (assignment_id) on delete cascade
);

create table if not exists Submission (
    submission_id bigserial primary key,
    user_id integer not null,
    assignment_id integer not null,
    points_earned integer,
    submit_date timestamp,
    student_comments text,
    grader_comments text,

    foreign key (user_id) references Users (user_id) on delete cascade,
    foreign key (assignment_id) references Assignment (assignment_id) on delete cascade
);

create table if not exists SubmissionUpload (
    user_id integer not null,
    submission_id integer not null,
    symlink text not null,

    foreign key (user_id) references Users (user_id) on delete cascade,
    foreign key (submission_id) references Submission (submission_id) on delete cascade
);

create table if not exists AssignmentUpload (
    user_id integer not null,
    assignment_id integer not null,
    symlink text not null,

    foreign key (user_id) references Users (user_id) on delete cascade,
    foreign key (assignment_id) references Assignment (assignment_id) on delete cascade
);
