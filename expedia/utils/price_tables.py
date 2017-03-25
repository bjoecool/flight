#!/usr/bin/env python3


def drop_temp_price_tables(file_name):
    with open(file_name) as f:
        for line in f.readlines():
            table_name = line.strip()
            table_name_t = table_name+'_t'
    
            tb_cmd='''drop table {0};'''.format(table_name_t)
            print(tb_cmd)

def insert_now_price_tables(file_name):
    with open(file_name) as f:
        for line in f.readlines():
            table_name = line.strip()
            table_name_t = table_name+'_t'
            seq_name = table_name+'_id'
    
            tb_cmd='''insert into {0}  (select nextval('{1}'),* from {2});'''.format(table_name,seq_name,table_name_t)
            print(tb_cmd)

def modify_price_table_name(file_name):
    with open(file_name) as f:
        for line in f.readlines():
            table_name = line.strip()
            new_table_name = table_name+'_t'
            tb_cmd = 'alter table '+ table_name+' rename to '+new_table_name+';';
            print(tb_cmd)
def main():
#     modify_price_table_name('price_tables.txt')
#     insert_now_price_tables('price_tables.txt')
    drop_temp_price_tables('price_tables.txt')
    
if __name__=='__main__':
    main()
