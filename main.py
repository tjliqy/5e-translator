import argparse
from app.core.utils import find_json_files, write_translate_cache, Job, FileWorkInfo
from app.core.translator import JsonAnalyser, JobProcessor, KnowledgeSetter, TermSetter, JobNeedTranslateSetter, ByHandHandler
from app.cli import transform_proofread, search_knowledge, compare_term, add_mysql_terms_to_redis, combine_temp_terms_to_csv,load_files_into_chroma_db, load_chm_files_into_chroma_db, load_term_from_text, transform_html_2_txt
from config import EN_PATH
from app.core.database import DBDictionary
import os
def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='function', required=True)
    
    # 为 transform 命令创建子解析器
    transform_parser = subparsers.add_parser('transform')
    
    # 为 translate 命令创建子解析器
    translate_parser = subparsers.add_parser('translate')
    translate_parser.add_argument('--en', default=EN_PATH,
                                  help='Path to the English data, default to the value in config')
    translate_parser.add_argument('--thread_num', default=10, type=int,
                                  help='Number of threads to use, default to 10')
    translate_parser.add_argument('--byhand', action='store_true', default=False,
                                  help='Whether to use by hand mode, default to False')

    translate_parser.add_argument('--force', action='store_true', default=False,
                                  help='Whether to force translate, update unproofreaded words, default to False')
    translate_parser.add_argument('--force-title', action='store_true', default=False,
                                  help='Whether to force translate, update unproofreaded titles, default to False')
    translate_parser.add_argument('--splited',  action='store_true', default=False,
                                  help='Whether to process splited data, default to False')
    
    search_parser = subparsers.add_parser('search')
    search_parser.add_argument('--query', default='', type=str,
                                  help='Search query')
    
    clean_parser = subparsers.add_parser('clean')
    clean_parser.add_argument('--en', default=EN_PATH,
                                help='Path to the English data, default to the value in config')
    
    #
    term_parser = subparsers.add_parser('term')
    term_parser.add_argument('--en', default=EN_PATH, type=str,
                                  help='Search term')
    term_parser.add_argument('--mode', default='add', type=str,
                                  help='Mode to use, default to add, can be add, dump or analyze')
    
    embed_parser = subparsers.add_parser('embed')
    embed_parser.add_argument('--dir', default='/data/DND5e_chm/艾伯伦：从终末战争中崛起', type=str,
                                  help='Path to the directory to embed')
    
    chm_parser = subparsers.add_parser('chm')
    chm_parser.add_argument('--dir', default='/data/DND5e_chm/', type=str,
                                  help='Path to the directory to embed')

    # 为 retry-failed 命令创建子解析器，用于从 failed_jobs.json 重试失败的 jobs
    retry_parser = subparsers.add_parser('retry-failed')
    retry_parser.add_argument('--file', required=True, type=str,
                              help='Path to the failed_jobs json file to retry')
    retry_parser.add_argument('--thread_num', default=10, type=int,
                              help='Number of threads to use, default to 10')
    retry_parser.add_argument('--byhand', action='store_true', default=False,
                              help='Whether to use by hand mode, default to False')

    
    args = parser.parse_args()
    
    # 从数据库中编码
    if args.function == 'transform':
        transform_proofread()
    # 数据解析流程
    elif args.function == 'translate':
        res = (find_json_files|JsonAnalyser()|JobNeedTranslateSetter()|KnowledgeSetter()|ByHandHandler()|TermSetter()|write_translate_cache|JobProcessor(args.thread_num, update=True)).invoke(args.en, config={'byhand': args.byhand, 'force': args.force, 'force_title': args.force_title, 'splited': args.splited})
        # res = (find_json_files|JsonAnalyser()|JobNeedTranslateSetter()|KnowledgeSetter()|ByHandHandler()|TermSetter()|write_translate_cache).invoke(args.en, config={'byhand': args.byhand, 'force': args.force, 'force_title': args.force_title, 'splited': args.splited})
        # res = (find_json_files|JsonAnalyser()|JobNeedTranslateSetter()|write_translate_cache|JobProcessor(args.thread_num, update=True)).invoke(args.en, config={'byhand': args.byhand, 'force': args.force})
        # res = (find_json_files|JsonAnalyser()|JobNeedTranslateSetter()|KnowledgeSetter()|ByHandHandler()|write_translate_cache).invoke(args.en, config={'byhand': args.byhand, 'force': args.force, 'force_title': args.force_title})
        for r in res:
            print(len(r.job_list), r.json_path)
    elif args.function == 'search':
        res = search_knowledge()
        print(res)
    elif args.function == 'clean':
        res = (find_json_files|JsonAnalyser()).invoke(args.en)
    elif args.function == 'term':
        if args.mode == 'add':
        # res = (find_json_files|TermFromJson()|AddTermCnFromDB()).invoke(args.en)
        # for t in res:
        #     print(t.category, t.en, t.cn)
            add_mysql_terms_to_redis()
        elif args.mode == 'dump':
            combine_temp_terms_to_csv()
        elif args.mode == 'analyze':
            for root, dirs, files in os.walk('/data/5e-translator/data'):
                for file in files:
                    if not file.endswith('.txt'):
                        continue
                    terms = load_term_from_text(os.path.join(root, file))
                    db = DBDictionary(conn_num=1)
                    for en,cn in terms.items():
                        db_bean = db.get(en,load_from_sql=True)
                        if db_bean is None:
                            print(f'{en} not found in db')
                        else:
                            if db_bean['proofread']:
                                print(f'{en} proofread, skip. db: {db_bean["cn"]}, text: {cn}')
                                continue
                            print(f'{en} 没有校对： db: {db_bean["cn"]}, text: {cn}')
                            if db_bean['cn'] == cn:
                                print(f'{en} 没有校对，但是 db 中的 cn 与 text 中的 cn 相同，自动校对')
                                db.update(db_bean['sql_id'], cn, proofread=True)
                                continue
                            resp = input(f'更新 {en} 为 {cn}? (Y/n): ')
                            if resp.strip() == 'skip':
                                continue
                            new_cn = cn
                            if resp.lower() != 'y' and resp.strip() != '':
                                new_cn = input('New cn: ')
                            db.update(db_bean['sql_id'], new_cn, proofread=True)
                                # print(f'{en} cn not match, db: {db_bean["cn"]}, text: {cn}')
        else:
            print('Unknown mode')
        # 输出术语
        # combine_temp_terms_to_csv()
    elif args.function == 'embed':
        load_files_into_chroma_db(args.dir)
        # load_chm_files_into_chroma_db('/data/DND5e_chm/艾伯伦：从终末战争中崛起')
    elif args.function == 'retry-failed':
        # 从失败文件中读取 jobs 并重试
        import json
        failed_file = args.file
        try:
            with open(failed_file, 'r') as fh:
                failed_list = json.load(fh)
        except Exception as e:
            print(f'无法读取失败文件: {e}')
            return

        jobs = []
        for jd in failed_list:
            try:
                j = Job(jd.get('uid'), jd.get('en_str'), jd.get('cn_str'), rel_path=jd.get('rel_path', ''), tag=jd.get('tag', ''), knowledge=jd.get('knowledge', []), current_names=jd.get('current_names', []), is_proofread=jd.get('is_proofread', False), sql_id=jd.get('sql_id', None), modified_at=jd.get('modified_at', 0))
                # j.err_time = 1
                # j.last_answer = jd.get('last_answer', '')
                # 保证需要翻译
                j.need_translate = True
                jobs.append(j)
            except Exception as e:
                print(f'构建 Job 失败: {e} - {jd}')

        if len(jobs) == 0:
            print('没有可重试的 Job')
            return

        # 使用已在文件顶部导入的 JobProcessor 重新处理这些 jobs
        # 把 jobs 包装成 FileWorkInfo，out_path 使用 failed 文件名的 basename 作为占位
        out_base = os.path.basename(failed_file)
        file_info = FileWorkInfo(jobs, {}, failed_file, os.path.join('retry', out_base))
        processor = JobProcessor(args.thread_num, update=True)
        # 注意：JobProcessor.invoke 内部通过 config['metadata'] 获取参数
        cfg = {'metadata': {'byhand': args.byhand, 'force': False, 'force_title': False, 'splited': True}}
        res = processor.invoke([file_info], config=cfg)
        for r in res:
            print(len(r.job_list), getattr(r, 'json_path', ''))
        
if __name__ == '__main__':
    main()