#!/usr/bin/python3

import os
import json
from openai import OpenAI


class TerminalChatBot:
    def __init__(
        self, api_key, model='gpt-3.5-turbo', messages=None, task=None
    ):
        self.api_key = api_key
        self.model = model
        self.messages = messages
        self.task = task
        self.user_info = {}
        self.current_step = 0

    def _set_message(self, role, content):
        self.messages.append({'role': role, 'content': content})

    def receive_message(self):
        return input('Вы: ')

    def send_message(self, message):
        print(f'Алёша: {message}')

    def query_llm(self):
        # return 'Рекомендация'
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", self.api_key))
        response = client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            temperature=0,
        )
        return response.choices[0].message.content

    def make_prompt(self):
        user_info_str = '\n'.join(
            f'{key}: {value}' for key, value in self.user_info.items()
        )
        return self.task[self.current_step]['content'].format(user_info=user_info_str)

    def next_question(self):
        if self.current_step < len(self.task):
            next_task = self.task[self.current_step]
            if next_task['target'] == 'user':
                return next_task['question']
            elif next_task['target'] == 'llm':
                prompt = self.make_prompt()
                self._set_message('user', prompt)
                response = self.query_llm()
                self._set_message('assistant', response)
                return response

    def run(self):
        while self.current_step < len(self.task):
            next_task = self.task[self.current_step]
            if next_task['target'] == 'system':
                self.send_message(self.task[self.current_step]['content'])
            elif next_task['target'] == 'user':
                content = self.task[self.current_step]['content']
                self._set_message('assistant', content)
                self.send_message(content)
                user_input = self.receive_message()
                self.user_info[next_task['key']] = user_input
                self._set_message('user', user_input)
            elif next_task['target'] == 'llm':
                prompt = self.make_prompt()
                self._set_message('user', prompt)
                content = self.query_llm()
                self._set_message('assistant', content)
                self.send_message(content)
            self.current_step += 1


def main():
    api_key = 'api_key'
    messages = [
        {
            'role': 'system',
            'content': 'Ты робот Алёша, эксперт и консультант по сноубордам.',
        }
    ]
    task = [
        {
            'content': 'Привет! Я робот Алёша. Помгоу вам с выбором сноуборда.',
            'target': 'system',
        },
        {
            'content': 'Как вас зовут?',
            'key': 'Имя',
            'target': 'user',
        },
        {
            'content': 'Сколько лет вы катаетесь на сноуборде?',
            'key': 'Опыт катания на сноуборде (лет)',
            'target': 'user',
        },
        {
            'content': 'Какая цель приобретения сноуборда?',
            'key': 'Цель приобретения сноуборда',
            'target': 'user',
        },
        {
            'content': 'Каков ваш бюджет?',
            'key': 'Бюджет',
            'target': 'user'},
        {
            'content': 'Есть ли у вас предпочтения по марке или модели?',
            'key': 'Предпочтения',
            'target': 'user',
        },
        {
            'content': 'Есть ли еще что-то, что вы хотите добавить?',
            'key': 'Дополнительная информация',
            'target': 'user',
        },
        {
            'content': 'Информация о покупателе:\n{user_info}\nДай рекомендацию по подходящему сноуборду.',
            'key': 'recommendation',
            'target': 'llm',
        },
        {
            'content': 'Благодарю за ответы!\nДо новых встречь!',
            'target': 'system',
        },
    ]
    bot = TerminalChatBot(
        api_key, model='gpt-3.5-turbo', messages=messages, task=task
    )
    bot.run()
    result = {
        'user_info': bot.user_info,
        'recommendation': bot.messages[-1]['content'],
    }
    return json.dumps(result)


if __name__ == '__main__':
    print(main())
