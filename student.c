#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#define STUD_FILE "students.txt"
#define CRE_FILE  "credentials.txt"
#define TEMP_FILE "temp.txt"

char currentUser[50];
char currentRole[20];

void read_line(char *buf, size_t size) {
    if (fgets(buf, (int)size, stdin) == NULL) {
        buf[0] = '\0';
        return;
    }
    size_t len = strlen(buf);
    if (len > 0 && buf[len - 1] == '\n') buf[len - 1] = '\0';
}

void trim(char *s) {
    char *start = s, *end;
    while (isspace((unsigned char)*start)) start++;
    if (start != s) memmove(s, start, strlen(start) + 1);
    if (*s == '\0') return;
    end = s + strlen(s) - 1;
    while (end > s && isspace((unsigned char)*end)) end--;
    *(end + 1) = '\0';
}


void ensure_credentials() {
    FILE *fp = fopen(CRE_FILE, "r");
    if (!fp) {
        fp = fopen(CRE_FILE, "w");
        if (!fp) {
            perror("Failed to create credentials file");
            return;
        }
        fprintf(fp, "admin admin admin\n");
        fprintf(fp, "student student student\n");
        fclose(fp);
        printf("Credentials file created with default users.\n");
    } else {
        fclose(fp);
    }
}

int username_exists(const char *username) {
    FILE *fp = fopen(CRE_FILE, "r");
    if (!fp) return 0;
    char line[256], u[100], p[100], r[50];
    while (fgets(line, sizeof(line), fp)) {
        trim(line);
        if (sscanf(line, "%99s %99s %49s", u, p, r) == 3) {
            if (strcmp(u, username) == 0) {
                fclose(fp);
                return 1;
            }
        }
    }
    fclose(fp);
    return 0;
}


int add_user_to_file(const char *username, const char *password, const char *role) {
    if (username_exists(username)) return 0;
    FILE *fp = fopen(CRE_FILE, "a");
    if (!fp) return 0;
    fprintf(fp, "%s %s %s\n", username, password, role);
    fclose(fp);
    return 1;
}


int remove_user_from_file(const char *username) {
    FILE *fp = fopen(CRE_FILE, "r");
    FILE *tmp = fopen(TEMP_FILE, "w");
    if (!fp || !tmp) {
        if (fp) fclose(fp);
        if (tmp) fclose(tmp);
        return 0;
    }

    char line[256], u[100], p[100], r[50];
    int found = 0;
    while (fgets(line, sizeof(line), fp)) {
        trim(line);
        if (sscanf(line, "%99s %99s %49s", u, p, r) == 3) {
            if (strcmp(u, username) == 0) {
                found = 1;
                continue; 
            }
            fprintf(tmp, "%s %s %s\n", u, p, r);
        }
    }

    fclose(fp);
    fclose(tmp);

    if (!found) {
        remove(TEMP_FILE);
        return 0;
    }

    if (remove(CRE_FILE) != 0) {
        perror("Failed to remove original credentials file");
        remove(TEMP_FILE);
        return 0;
    }
    if (rename(TEMP_FILE, CRE_FILE) != 0) {
        perror("Failed to rename credentials temp file");
        return 0;
    }
    return 1;
}


int update_password_in_file(const char *username, const char *newpass) {
    FILE *fp = fopen(CRE_FILE, "r");
    FILE *tmp = fopen(TEMP_FILE, "w");
    if (!fp || !tmp) {
        if (fp) fclose(fp);
        if (tmp) fclose(tmp);
        return 0;
    }
    char line[256], u[100], p[100], r[50];
    int found = 0;
    while (fgets(line, sizeof(line), fp)) {
        trim(line);
        if (sscanf(line, "%99s %99s %49s", u, p, r) == 3) {
            if (strcmp(u, username) == 0) {
                fprintf(tmp, "%s %s %s\n", u, newpass, r);
                found = 1;
            } else {
                fprintf(tmp, "%s %s %s\n", u, p, r);
            }
        }
    }
    fclose(fp);
    fclose(tmp);
    if (!found) {
        remove(TEMP_FILE);
        return 0;
    }
    if (remove(CRE_FILE) != 0) {
        perror("Failed to remove original credentials file");
        remove(TEMP_FILE);
        return 0;
    }
    if (rename(TEMP_FILE, CRE_FILE) != 0) {
        perror("Failed to rename credentials temp file");
        return 0;
    }
    return 1;
}


int login() {
    char u[50], p[50];
    ensure_credentials();

    printf("USERNAME: ");
    read_line(u, sizeof(u));
    trim(u);
    printf("PASSWORD: ");
    read_line(p, sizeof(p));
    trim(p);

    FILE *fp = fopen(CRE_FILE, "r");
    if (!fp) {
        printf("Credential file missing!\n");
        return 0;
    }

    char line[200], fu[100], fpw[100], fr[50];
    while (fgets(line, sizeof(line), fp)) {
        trim(line);
        if (sscanf(line, "%99s %99s %49s", fu, fpw, fr) == 3) {
            if (strcmp(u, fu) == 0 && strcmp(p, fpw) == 0) {
                strcpy(currentUser, fu);
                strcpy(currentRole, fr);
                fclose(fp);
                return 1;
            }
        }
    }

    fclose(fp);
    return 0;
}



void addStudent() {
    char buf[100], name[100];
    int roll;
    float mark;

    printf("Roll: ");
    read_line(buf, sizeof(buf));
    roll = atoi(buf);

    printf("Name: ");
    read_line(name, sizeof(name));
    trim(name);

    printf("Mark: ");
    read_line(buf, sizeof(buf));
    mark = atof(buf);

    FILE *fp = fopen(STUD_FILE, "a");
    if (!fp) {
        perror("Error opening student file");
        return;
    }

    fprintf(fp, "%d|%s|%.2f\n", roll, name, mark);
    fclose(fp);

    printf("Student added successfully.\n");
}

void displayStudents() {
    FILE *fp = fopen(STUD_FILE, "r");
    if (!fp) {
        printf("No student file found.\n");
        return;
    }

    printf("\nRoll\tName\tMark\n");
    printf("----------------------------\n");

    char line[200], name[100];
    int roll;
    float mark;

    while (fgets(line, sizeof(line), fp)) {
        if (sscanf(line, "%d|%99[^|]|%f", &roll, name, &mark) == 3) {
            printf("%d\t%s\t%.2f\n", roll, name, mark);
        }
    }

    fclose(fp);
}

void searchStudent() {
    char buf[50];
    int find;
    printf("Enter roll: ");
    read_line(buf, sizeof(buf));
    find = atoi(buf);

    FILE *fp = fopen(STUD_FILE, "r");
    if (!fp) {
        printf("Student file missing.\n");
        return;
    }

    char line[200], name[100];
    int roll;
    float mark;

    while (fgets(line, sizeof(line), fp)) {
        if (sscanf(line, "%d|%99[^|]|%f", &roll, name, &mark) == 3) {
            if (roll == find) {
                printf("Found: %d | %s | %.2f\n", roll, name, mark);
                fclose(fp);
                return;
            }
        }
    }

    fclose(fp);
    printf("Student not found.\n");
}

void updateStudent() {
    char buf[100], line[200], name[100];
    int roll, updateRoll;
    float mark;

    printf("Roll to update: ");
    read_line(buf, sizeof(buf));
    updateRoll = atoi(buf);

    FILE *fp = fopen(STUD_FILE, "r");
    FILE *temp = fopen(TEMP_FILE, "w");

    if (!fp || !temp) {
        printf("Error opening file.\n");
        if (fp) fclose(fp);
        if (temp) fclose(temp);
        return;
    }

    int found = 0;
    while (fgets(line, sizeof(line), fp)) {
        if (sscanf(line, "%d|%99[^|]|%f", &roll, name, &mark) == 3) {
            if (roll == updateRoll) {
                found = 1;

                printf("New Name: ");
                read_line(name, sizeof(name));
                trim(name);

                printf("New Mark: ");
                read_line(buf, sizeof(buf));
                mark = atof(buf);

                fprintf(temp, "%d|%s|%.2f\n", roll, name, mark);
            } else {
                fprintf(temp, "%s", line);
            }
        }
    }

    fclose(fp);
    fclose(temp);

    remove(STUD_FILE);
    rename(TEMP_FILE, STUD_FILE);

    if (found) printf("Record updated.\n");
    else printf("Roll not found.\n");
}

void deleteStudent() {
    char buf[50], line[200], name[100];
    int roll, delRoll;
    float mark;

    printf("Roll to delete: ");
    read_line(buf, sizeof(buf));
    delRoll = atoi(buf);

    FILE *fp = fopen(STUD_FILE, "r");
    FILE *temp = fopen(TEMP_FILE, "w");

    if (!fp || !temp) {
        if (fp) fclose(fp);
        if (temp) fclose(temp);
        printf("Error opening file.\n");
        return;
    }

    int found = 0;

    while (fgets(line, sizeof(line), fp)) {
        if (sscanf(line, "%d|%99[^|]|%f", &roll, name, &mark) == 3) {
            if (roll != delRoll) {
                fprintf(temp, "%s", line);
            } else {
                found = 1;
            }
        }
    }

    fclose(fp);
    fclose(temp);

    remove(STUD_FILE);
    rename(TEMP_FILE, STUD_FILE);

    if (found) printf("Student deleted.\n");
    else printf("Roll not found.\n");
}


void createUserAdmin() {
    char uname[100], pass[100], role[50];

    printf("New username: ");
    read_line(uname, sizeof(uname));
    trim(uname);
    if (uname[0] == '\0') { printf("Invalid username.\n"); return; }
    if (username_exists(uname)) { printf("Username already exists.\n"); return; }

    printf("New password: ");
    read_line(pass, sizeof(pass));
    trim(pass);
    if (pass[0] == '\0') { printf("Invalid password.\n"); return; }

    printf("Role (admin/student): ");
    read_line(role, sizeof(role));
    trim(role);
    if (strcmp(role, "admin") != 0 && strcmp(role, "student") != 0) {
        printf("Invalid role. Must be 'admin' or 'student'.\n");
        return;
    }

    if (add_user_to_file(uname, pass, role)) {
        printf("User '%s' created with role '%s'.\n", uname, role);
    } else {
        printf("Failed to create user.\n");
    }
}

void deleteUserAdmin() {
    char uname[100];

    printf("Username to delete: ");
    read_line(uname, sizeof(uname));
    trim(uname);
    if (uname[0] == '\0') { printf("Invalid username.\n"); return; }

    if (strcmp(uname, currentUser) == 0) {
        printf("You cannot delete your own account while logged in.\n");
        return;
    }

    if (!username_exists(uname)) {
        printf("User does not exist.\n");
        return;
    }

    if (remove_user_from_file(uname)) {
        printf("User '%s' removed.\n", uname);
    } else {
        printf("Failed to remove user '%s'.\n", uname);
    }
}

void changePassword() {
    char newpass[100];
    printf("Enter new password: ");
    read_line(newpass, sizeof(newpass));
    trim(newpass);
    if (newpass[0] == '\0') { printf("Invalid password.\n"); return; }

    if (update_password_in_file(currentUser, newpass)) {
        printf("Password updated for user '%s'. Please re-login to confirm changes.\n", currentUser);
       
    } else {
        printf("Failed to update password.\n");
    }
}



void adminMenu() {
    while (1) {
        printf("\nADMIN MENU\n");
        printf("1. Add Student\n2. Display Students\n3. Search Student\n4. Update Student\n5. Delete Student\n");
        printf("6. Create User\n7. Delete User\n8. Change My Password\n9. Logout\n");
        printf("Choice: ");
        char buf[10];
        read_line(buf, sizeof(buf));
        int c = atoi(buf);

        switch (c) {
            case 1: addStudent(); break;
            case 2: displayStudents(); break;
            case 3: searchStudent(); break;
            case 4: updateStudent(); break;
            case 5: deleteStudent(); break;
            case 6: createUserAdmin(); break;
            case 7: deleteUserAdmin(); break;
            case 8: changePassword(); break;
            case 9: return;
            default: printf("Invalid choice.\n");
        }
    }
}

void studentMenu() {
    while (1) {
        printf("\nSTUDENT MENU\n");
        printf("1. Display Students\n2. Search Student\n3. Change My Password\n4. Logout\n");
        printf("Choice: ");
        char buf[10];
        read_line(buf, sizeof(buf));
        int c = atoi(buf);

        switch (c) {
            case 1: displayStudents(); break;
            case 2: searchStudent(); break;
            case 3: changePassword(); break;
            case 4: return;
            default: printf("Invalid choice.\n");
        }
    }
}



int main() {
    if (!login()) {
        printf("Invalid login!\n");
        return 0;
    }


    if (strcmp(currentRole, "admin") == 0) {
        printf("Logged in as admin: %s\n", currentUser);
        adminMenu();
    } else if (strcmp(currentRole, "student") == 0) {
        printf("Logged in as student: %s\n", currentUser);
        studentMenu();
    } else {
        printf("Access denied: Only admin and student allowed.\n");
    }

    printf("Goodbye.\n");
    return 0;
}