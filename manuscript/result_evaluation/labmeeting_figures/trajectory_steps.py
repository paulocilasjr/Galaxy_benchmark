"""Turn a run's job ledger into the sequence of analysis steps it executed, with one label per step.

Both conditions are labelled with the same vocabulary, so that replicates can be compared within a condition and the
two conditions can be read side by side:
- a named tool keeps its name: a Galaxy tool id ('kraken2', 'bedtools_intersectbed') or a program, with its
  subcommand for multi-command programs ('minimap2', 'bedtools intersect', 'samtools view');
- a custom script is labelled by its language and the non-standard-library modules it imports: 'py:pandas+scanpy',
  'R:DESeq2'; a Galaxy user-defined tool (UDT, a tool the agent wrote and ran inside Galaxy) is labelled by its
  container and main command, 'UDT:anndata/python', 'UDT:hdf5/h5dump', the counterpart of a script's imports;
- table and text utilities keep their names as well (Cut1, Filter1, datamash_ops in Galaxy; awk, sort, cut, grep,
  jq on the command line), and a command made only of them is labelled by the first one;
- plumbing is dropped in both conditions: data upload and fetch, format converters and Galaxy's internal tools,
  downloads and installs, and commands that only inspect files (ls, head, wc, ...).

Galaxy steps are the jobs Galaxy executed (execution_location 'galaxy_job'), whatever route the agent used to start
them, in order of job creation time (the ledgers list them in another order). Custom-code steps are the shell commands the ledger classes as analysis or input preparation.
"""
import json
import re
import sys

STDLIB = set(sys.stdlib_module_names) | {'__future__'}

# Galaxy tools that only move, convert or reshape data
GALAXY_PLUMBING = re.compile(r'^(__.*__|upload1|CONVERTER_.*|.*_to_tabular|tabular_to_csv|.*converter.*|'
                             r'Convert characters1|ucsc_bigwig.*)$', re.I)
# Galaxy's own tools outside the Tool Shed; any other id outside the Tool Shed is a tool the agent defined (a UDT,
# registered through the UDT tool or through the API)
GALAXY_BUILTIN = {'Cut1', 'Filter1', 'Grep1', 'Grouping1', 'join1', 'sort1', 'cat1', 'Count1', 'wc_gnu', 'mergeCols1',
                  'Show beginning1', 'Show tail1', 'Remove beginning1', 'Paste1', 'addValue', 'comp1',
                  'Summary_Statistics1', 'Convert characters1', 'ChangeCase', 'Extract_features1', 'random_lines1',
                  'createInterval', 'gene2exon1', 'gff2bed1', 'liftOver1', 'gops_intersect_1', 'subtract_query1',
                  'MAF_To_Fasta1', 'Extract genomic DNA 1', 'ucsc_table_direct1', 'ucsc_bigbedtobed', 'bigwigtowig',
                  'wiggle2simple1', 'gff_filter_by_attribute', 'gtf_filter_by_attribute_values_list',
                  'secure_hash_message_digest', 'lped2pbedconvert', 'qual_stats_boxplot', 'fastq_groomer',
                  'sam_bw_filter', 'tophat', 'csv_to_tabular', 'tabular_to_csv', 'upload1'}


def galaxy_builtin(tool):
    return tool in GALAXY_BUILTIN or ' ' in tool or tool.startswith(('CONVERTER_', '__', 'interactive_tool_', 'hgv_'))

# command-line programs
INSPECT = {'ls', 'head', 'tail', 'cat', 'wc', 'echo', 'pwd', 'file', 'du', 'df', 'stat', 'find', 'which', 'command',
           'printf', 'sleep', 'ps', 'true', 'false', 'test', '[', '[[', 'cd', 'mkdir', 'rm', 'cp', 'mv', 'ln', 'touch',
           'chmod', 'tee', 'xargs', 'basename', 'dirname', 'realpath', 'readlink', 'env', 'export', 'set', 'uname',
           'nproc', 'free', 'date', 'md5sum', 'sha256sum', 'less', 'more', 'column', 'nl', 'od', 'xxd', 'hexdump',
           'strings', 'diff', 'cmp', 'comm', 'tree', 'type', 'hash', 'ulimit', 'timeout', 'kill', 'wait', 'source',
           '.', 'exit', 'return', 'local', 'declare', 'read', 'shift', 'for', 'while', 'if', 'then', 'else', 'elif',
           'fi', 'do', 'done', 'case', 'esac', '{', '}', '(', ')', 'trap', 'unset', 'let', 'eval', 'exec', 'nohup',
           'time', 'sudo', 'whoami', 'id', 'hostname', 'top', 'lscpu', 'jobs', 'disown', 'pgrep', 'pkill', 'until',
           'in', 'function', 'mktemp', 'sync', 'yes', 'tput', 'clear', 'apropos', 'man', 'help', 'getconf'}
PASS = {'gzip', 'gunzip', 'zcat', 'bzip2', 'bunzip2', 'xz', 'unxz', 'pigz', 'zstd', 'bzcat', 'xzcat', 'zless'}
FETCH = {'curl', 'wget', 'git', 'pip', 'pip3', 'conda', 'mamba', 'micromamba', 'apt', 'apt-get', 'tar', 'unzip', 'zip',
         'prefetch', 'fasterq-dump', 'fastq-dump', 'aws', 'gsutil', 'rsync', 'scp', 'ftp', 'lftp', 'aria2c',
         'update_blastdb.pl', 'npm', 'cargo', 'R_install', 'install.packages'}
TEXT = {'awk', 'gawk', 'mawk', 'sort', 'uniq', 'cut', 'sed', 'tr', 'join', 'paste', 'grep', 'egrep', 'fgrep', 'rg',
        'jq', 'datamash', 'bc', 'expr', 'seq', 'shuf', 'split', 'csvtk', 'mlr', 'perl', 'fold', 'rev', 'tac',
        'numfmt', 'printenv', 'yq', 'xmllint', 'iconv', 'dos2unix'}
SUBCOMMAND = {'samtools', 'bedtools', 'bcftools', 'gatk', 'picard', 'seqkit', 'bwa', 'bwa-mem2', 'tabix', 'plink',
              'plink2', 'vcftools', 'datasets', 'efetch', 'esearch', 'esummary', 'elink', 'kraken2', 'bowtie2-build',
              'salmon', 'kallisto', 'macs2', 'macs3', 'deeptools', 'homer', 'meme', 'blastdbcmd', 'ncbi-datasets',
              'snpEff', 'vep', 'cellranger', 'star', 'STAR', 'hisat2-build', 'featureCounts', 'phykit', 'mafft',
              'iqtree', 'iqtree2', 'trimal', 'diamond', 'mmseqs', 'sra-stat', 'bigWigAverageOverBed', 'liftOver'}
NOT_PROGRAMS = {'print', 'next', 'EOF', 'END', 'BEGIN', 'PY', 'X', 'n++', 'i++', 'last', 'length', 'getline',
                'gene', 'exon', 'genotype', 'else:', 'try:', 'except', 'import', 'from', 'def', 'with'}
ENTREZ = {'efetch', 'esearch', 'esummary', 'elink', 'datasets', 'ncbi-datasets'}   # remote queries: data fetch


def galaxy_label(tool):
    t = tool.split('/')[-2] if tool.startswith('toolshed.') else tool
    if GALAXY_PLUMBING.match(t) or GALAXY_PLUMBING.match(tool):
        return None
    return t


def script_label(lang, body):
    if lang == 'py':
        mods = re.findall(r'^\s*(?:from\s+([A-Za-z_]\w*)|import\s+([A-Za-z_][\w, .]*))', body, re.M)
        names = set()
        for frm, imp in mods:
            for m in ([frm] if frm else [x.strip().split(' ')[0] for x in imp.split(',')]):
                if m:
                    names.add(m.split('.')[0])
        libs = sorted(n for n in names if n not in STDLIB)
    else:
        libs = sorted(set(re.findall(r'(?:library|require|requireNamespace)\(\s*["\']?([A-Za-z][\w.]*)', body)))
    return f'{lang}:' + '+'.join(libs) if libs else lang


HEREDOC = re.compile(r"<<-?\s*(['\"]?)(\w+)\1[^\n]*\n(.*?)\n[ \t]*\2[ \t]*(?=\n|$)", re.S)
WRITE = re.compile(r"(?:cat|tee)\s*>+\s*['\"]?([^\s'\"<>;|&]+)['\"]?\s*<<-?\s*(['\"]?)(\w+)\2[^\n]*\n(.*?)\n[ \t]*\3[ \t]*(?=\n|$)",
                   re.S)
PYTHON = re.compile(r"(?:^|[\s;|&(`])(?:python3?(?:\.\d+)?|ipython)(?=\s|$)((?:\s+-[A-Za-z]+)*)\s*(\S*)", re.M)
RSCRIPT = re.compile(r"(?:^|[\s;|&(`])(?:Rscript|R)(?=\s)((?:\s+-{1,2}[\w-]+)*)\s*(\S*)", re.M)


def unwrap(command):
    if not isinstance(command, str):                         # an argv list
        command = ' '.join(map(str, command)) if isinstance(command, (list, tuple)) else str(command)
    m = re.match(r"^(?:/usr)?(?:/bin/)?(?:ba)?sh\s+-l?c\s+(.*)$", command, re.S)
    if not m:
        return command
    body = m.group(1).strip()
    if len(body) >= 2 and body[0] == body[-1] and body[0] in '\'"':
        body = body[1:-1]
    return body.replace("'\"'\"'", "'")


def shell_label(command, scripts=None):
    """One label for one shell command: a script, else the first named program, else the first table or text utility;
    None for plumbing.
    `scripts` maps file names written earlier in the run (cat > x.py <<EOF) to their contents."""
    scripts = {} if scripts is None else scripts
    body = unwrap(command)
    for path, _, _, content in WRITE.findall(body):
        scripts[path.split('/')[-1]] = content
    bare = HEREDOC.sub('<<HEREDOC', body)                     # the command without heredoc contents
    for rx, lang in ((PYTHON, 'py'), (RSCRIPT, 'R')):
        for flags, target in rx.findall(bare):
            if lang == 'R' and target.startswith('CMD'):
                continue
            if '-c' in flags.split() or target in ('-', '<<HEREDOC', '') or target.startswith('<<'):
                return script_label(lang, body)              # inline code or heredoc: its imports are in the body
            name = target.strip('\'"').split('/')[-1]
            if name in scripts:
                return script_label(lang, scripts[name])
            return script_label(lang, body) if lang == 'py' and 'import ' in body else lang
    if WRITE.search(body) and not re.sub(WRITE, '', body).strip():
        return None                                          # only writes a file
    # quoted arguments (awk programs, grep patterns, URLs) are not commands
    bare = re.sub(r"'[^']*'", "''", bare)
    for _ in range(3):                                       # awk and perl blocks whose quoting the wrapper mangled
        bare = re.sub(r'\{[^{}]*\}', '', bare)
    bare = re.sub(r'"(?:\\.|[^"\\])*"', '""', bare)
    named, text = None, None
    for seg in re.split(r"\|\||&&|\||;|\n|\$\(|`", bare):
        words = seg.strip().split()
        while words and ('=' in words[0] and not words[0].startswith('-') or words[0] in
                         ('time', 'sudo', 'nohup', 'env', 'then', 'do', 'else', '{', '(', '!', 'exec', 'xargs')):
            words = words[1:]
        if len(words) > 1 and words[0].split('/')[-1] in ('micromamba', 'mamba', 'conda') and words[1] == 'run':
            words = words[2:]                                 # micromamba run -p ENV tool ... -> tool ...
            while words and words[0].startswith('-'):
                words = words[2:] if words[0] in ('-p', '-n', '--prefix', '--name') else words[1:]
        if not words:
            continue
        prog = words[0].split('/')[-1].strip('\'"(){}')
        if not prog or prog in INSPECT or prog in PASS or prog.startswith(('-', '$', '#', '>', '<')):
            continue
        if prog in FETCH or prog in ENTREZ or prog in NOT_PROGRAMS or prog.endswith(('++', '--')):
            continue                                         # (counters like removed++ come from awk programs)
        if prog in TEXT:
            text = text or prog
            continue
        if not re.match(r'^[A-Za-z][\w.+-]*$', prog) or '.' in prog and not prog.endswith(('.pl', '.sh')):
            continue
        if re.match(r'^(python3?(\.\d+)?|ipython)$', prog):
            return 'py'
        if prog in ('Rscript', 'R'):
            return 'R'
        if prog in SUBCOMMAND and len(words) > 1 and re.match(r'^[a-z][\w-]*$', words[1]):
            prog = f'{prog} {words[1]}'
        named = named or prog
    return named or text


def udt_label(rep):
    """'UDT:<container>/<main command>' from a UDT definition."""
    container = rep.get('container') or ''
    if isinstance(container, dict):                          # {'type': 'docker', 'image': ...} and similar
        container = container.get('image') or container.get('identifier') or next(
            (v for v in container.values() if isinstance(v, str) and ('/' in v or ':' in v)), '')
    image = str(container).split('/')[-1]
    name, _, tag = image.partition(':')
    if name == 'udt':                                        # the benchmark's own UDT images: name the toolbox
        name = '-'.join(tag.split('-')[:2])
    name = re.sub(r'^(r|bioconductor)-', 'R-', name)
    cmd = shell_label(rep.get('shell_command') or '') or ''
    main = cmd.split(':')[0] if cmd.startswith(('py', 'R')) else cmd
    return 'UDT:' + '/'.join(x for x in (name, main) if x)


def steps(ledger_path, env):
    """The labelled analysis steps of one run, in execution order."""
    d = json.load(open(ledger_path))
    # the UDTs this run registered; any other kebab-case id outside the Tool Shed is also an agent-written tool
    udts = {}
    for e in d['events']:
        rep = (e.get('parameters') or {}).get('representation') if isinstance(e.get('parameters'), dict) else None
        if e.get('tool') == 'run_galaxy_udt_and_wait' and isinstance(rep, dict) and rep.get('id'):
            udts[rep['id']] = udt_label(rep)
    scripts, out = {}, []
    events = d['events']
    if env == 'galaxy':                                      # Galaxy jobs in creation order; agent events keep theirs
        events = sorted((e for e in events if e.get('execution_location') == 'galaxy_job'),
                        key=lambda e: (e.get('timestamp') or '', e.get('sequence') or 0))
    for e in events:
        if env == 'galaxy':
            if e.get('execution_location') != 'galaxy_job' or not e.get('tool'):
                continue
            if e.get('event_type') == 'input_acquisition':
                continue
            tool = e['tool']
            if tool in udts:
                label = udts[tool]
            elif not tool.startswith('toolshed.') and not galaxy_builtin(tool):
                label = 'UDT'
            else:
                label = galaxy_label(tool)
        else:
            if e.get('tool') != 'shell' or e.get('event_type') not in ('analysis', 'input_preparation'):
                continue
            label = shell_label(e.get('command') or '', scripts)
        if label:
            out.append(label)
    return out
