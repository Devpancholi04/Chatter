import random
import string
from datetime import datetime
from django.utils.text import slugify


class generate_ids:

    def gen_user_id(self, first_name):
        userId = f"{first_name}{datetime.now().strftime('%Y%m%d:%H%M%S')}--{"".join(random.choice(string.digits) for _ in range(5))}"
        return slugify(userId)


    def gen_mess_id(self):
        mess_id = f"mss{"".join(random.choice(string.digits) for _ in range(5))}"
        return slugify(mess_id)
    
    def gen_group_id(self, name):
        group_id = f"Group-{name}{random.randint(10000,99999)}"
        return slugify(group_id)

if __name__ == "__main__":
    a = generate_ids()
    a.gen_user_id('dev')
    print(a.gen_mess_id())
    print(a.gen_group_id('dev'))
    