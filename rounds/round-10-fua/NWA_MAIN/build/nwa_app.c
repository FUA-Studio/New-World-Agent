/* NWA 单文件启动器：内嵌全部源码(nwa_b64.h)，首跑解包到 $HOME/.nwa_pkg，
   然后 exec python 运行指定入口。
   构建:
     Linux ELF : gcc -O2 -DENTRY='"main.py"'   -o nwa-linux     nwa_app.c
     Linux GUI : gcc -O2 -DENTRY='"nwa_gui.py"' -o nwa-gui-linux nwa_app.c
     Windows   : x86_64-w64-mingw32-gcc -O2 -DENTRY='"main.py"'   -o nwa-win.exe nwa_app.c
                 x86_64-w64-mingw32-g++ -O2 -DENTRY='"nwa_gui.py"' -o nwa-gui-win.exe nwa_app.c
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>

#ifdef _WIN32
#include <direct.h>
#define SLASH "\\"
#else
#include <unistd.h>
#define SLASH "/"
#endif

#ifndef ENTRY
#define ENTRY "main.py"
#endif

#include "nwa_b64.h"   /* static const char NWA_B64[] */

static int b64val(int c) {
    if (c >= 'A' && c <= 'Z') return c - 'A';
    if (c >= 'a' && c <= 'z') return c - 'a' + 26;
    if (c >= '0' && c <= '9') return c - '0' + 52;
    if (c == '+') return 62;
    if (c == '/') return 63;
    return -1;
}

static size_t b64decode(const char *in, char *out) {
    size_t o = 0;
    int a = 0, bits = 0;
    for (const char *p = in; *p; p++) {
        int v = b64val((unsigned char)*p);
        if (v < 0) continue;      /* 跳过 '=' 与换行 */
        a = (a << 6) | v;
        bits += 6;
        if (bits >= 8) {
            bits -= 8;
            out[o++] = (unsigned char)((a >> bits) & 0xFF);
            a &= (1 << bits) - 1; /* 清掉已输出的高位 */
        }
    }
    return o;
}

static void mkdir_p(const char *path) {
    char buf[1024];
    snprintf(buf, sizeof buf, "%s", path);
    for (char *p = buf + 1; *p; p++) {
        if (*p == '/' || *p == '\\') {
            char save = *p;
            *p = 0;
#ifdef _WIN32
            _mkdir(buf);
#else
            mkdir(buf, 0755);
#endif
            *p = save;
        }
    }
#ifdef _WIN32
    _mkdir(buf);
#else
    mkdir(buf, 0755);
#endif
}

int main(int argc, char **argv) {
    const char *home = getenv("HOME");
    if (!home) home = ".";
    char pkg[1024];
    snprintf(pkg, sizeof pkg, "%s/.nwa_pkg", home);
    mkdir_p(pkg);

    /* 内嵌数据: 每行 "relpath<TAB>base64" */
    int wrote = 0;
    char line[1 << 20];
    for (const char *p = NWA_B64; *p; ) {
        char *nl = strchr(p, '\n');
        size_t llen = nl ? (size_t)(nl - p) : strlen(p);
        if (llen > sizeof line - 1) break;
        memcpy(line, p, llen);
        line[llen] = 0;
        p = nl ? nl + 1 : p + llen;
        char *tab = strchr(line, '\t');
        if (!tab) continue;
        *tab = 0;
        char full[1400];
        snprintf(full, sizeof full, "%s%s%s", pkg, SLASH, line);
        char *sl = strrchr(full, '/');
        if (!sl) sl = strrchr(full, '\\');
        if (sl && sl != full) {
            char save = *sl;
            *sl = 0;
            mkdir_p(full);      /* 截断后 full 即父目录 */
            *sl = save;
        }
        char *b64 = tab + 1;
        char outbuf[1 << 20];
        size_t n = b64decode(b64, outbuf);
        FILE *f = fopen(full, "wb");
        if (f) {
            if (n) fwrite(outbuf, 1, n, f);
            fclose(f);
            wrote++;
        }
    }
    if (!wrote) {
        fprintf(stderr, "nwa: 内嵌包体解包失败\n");
        return 1;
    }

    char entry[1500];
    snprintf(entry, sizeof entry, "%s%s%s", pkg, SLASH, ENTRY);

    size_t narg = 2 + (size_t)argc;
    char **cmd = calloc(narg, sizeof(char *));
    int k = 0;
#ifdef _WIN32
    cmd[k++] = "python3";
#else
    cmd[k++] = "python3";
#endif
    cmd[k++] = entry;
    for (int i = 1; i < argc; i++) cmd[k++] = argv[i];
    cmd[k] = 0;

    fflush(stdout);
    fflush(stderr);
#ifdef _WIN32
    _execvp("python3", cmd);
    for (int i = 0; i < narg; i++) free(cmd[i]);
    free(cmd);
    cmd = calloc(2 + argc, sizeof(char *));
    k = 0;
    cmd[k++] = "python";
    cmd[k++] = entry;
    for (int i = 1; i < argc; i++) cmd[k++] = argv[i];
    cmd[k] = 0;
    _execvp("python", cmd);
#else
    execvp("python3", cmd);
#endif
    fprintf(stderr, "nwa: 未找到 python（请先安装 Python 3）\n");
    return 127;
}
