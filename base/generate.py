import random
import string
from datetime import datetime
from django.utils.text import slugify


class generate_ids:

    def gen_user_id(self, first_name):
        userId = f"{first_name}{datetime.now().strftime('%Y%m%d:%H%M%S')}--{"".join(random.choice(string.digits) for _ in range(5))}"
        return slugify(userId)



if __name__ == "__main__":
    a = generate_ids()
    a.gen_user_id('dev')