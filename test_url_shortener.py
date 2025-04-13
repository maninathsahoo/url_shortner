import unittest
import hashlib
from app import app, generate_short_code, get_domain


class TestURLShortener(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        # Clear storage for each test
        app.config['url_mapping'] = {}
        app.config['url_to_code'] = {}
        app.config['domain_counts'] = {}

    # Helper functions tests
    def test_generate_short_code(self):
        url = "https://www.amazon.in/?&tag=googhydrabk1-21&ref=pd_sl_7hz2t19t5c_e&adgrpid=155259815513&hvpone=&hvptwo=&hvadid=674842289437&hvpos=&hvnetw=g&hvrand=915503101757116898&hvqmt=e&hvdev=c&hvdvcmdl=&hvlocint=&hvlocphy=9061995&hvtargid=kwd-10573980&hydadcr=14453_2316415&gad_source=1"
        code = generate_short_code(url)
        self.assertEqual(len(code), 6)
        self.assertEqual(code, hashlib.md5(url.encode()).hexdigest()[:6])

    def test_get_domain(self):
        self.assertEqual(get_domain("https://www.amazon.in/?&tag=googhydrabk1-21&ref=pd_sl_7hz2t19t5c_e&adgrpid=155259815513&hvpone=&hvptwo=&hvadid=674842289437&hvpos=&hvnetw=g&hvrand=915503101757116898&hvqmt=e&hvdev=c&hvdvcmdl=&hvlocint=&hvlocphy=9061995&hvtargid=kwd-10573980&hydadcr=14453_2316415&gad_source=1"), "www.amazon.in")
        self.assertEqual(get_domain("http://sub.example.com"), "sub.example.com")
        self.assertEqual(get_domain("invalid_test_url"), "invalid_domain")

    # API endpoint tests
    def test_shorten_url(self):
        # Test valid URL
        response = self.app.post(
            '/api/shorten',
            json={'url': 'https://www.amazon.in/Samsung-Inverter-Fully-Automatic-WA70BG4441YYTL-Technology/dp/B0B8NHX62W/ref=sr_1_1_sspa?_encoding=UTF8&content-id=amzn1.sym.58c90a12-100b-4a2f-8e15-7c06f1abe2be&dib=eyJ2IjoiMSJ9.huIQjSkTuPfYXaUe3MtXkWA0dLO881tU6BS-vQHVB7xaMA60pMktorrxmEyRqWEGCADjTzT6-Ms0sEt3mT0MLyDQnRahJyJyZaII_78nYnwEtKMc60dVzzY7DBBR1pmXrLcot0Iar6_Bvz7hkBDpAr0rs91x3qYLYIJNlMWmub_NY_qnRbMnClPrYAQ0bd1Rhrkj6_K76vH3eMjifIwIktuEvdGyQ-EuhIwUohFKABH28_Q1eZ8Vn6nalhZPE_LH3qwIq5xpSAnsWpSo-pCgr5zQ9Rlw_6fo78-A4H_wTtA.o72xj55DclBp_H4i3pzFKAH06yOd8M5yLUHTO0IXrrE&dib_tag=se&pd_rd_r=8635ba35-03eb-4884-ae60-d61a94825127&pd_rd_w=R921o&pd_rd_wg=Fcshv&qid=1744561214&refinements=p_85%3A10440599031&rps=1&s=kitchen&sr=1-1-spons&sp_csd=d2lkZ2V0TmFtZT1zcF9hdGZfYnJvd3Nl&th=1'}
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('short_url', data)

        # Test duplicate URL returns same short code
        response2 = self.app.post(
            '/api/shorten',
            json={'url': 'https://www.amazon.in/Samsung-Inverter-Fully-Automatic-WA70BG4441YYTL-Technology/dp/B0B8NHX62W/ref=sr_1_1_sspa?_encoding=UTF8&content-id=amzn1.sym.58c90a12-100b-4a2f-8e15-7c06f1abe2be&dib=eyJ2IjoiMSJ9.huIQjSkTuPfYXaUe3MtXkWA0dLO881tU6BS-vQHVB7xaMA60pMktorrxmEyRqWEGCADjTzT6-Ms0sEt3mT0MLyDQnRahJyJyZaII_78nYnwEtKMc60dVzzY7DBBR1pmXrLcot0Iar6_Bvz7hkBDpAr0rs91x3qYLYIJNlMWmub_NY_qnRbMnClPrYAQ0bd1Rhrkj6_K76vH3eMjifIwIktuEvdGyQ-EuhIwUohFKABH28_Q1eZ8Vn6nalhZPE_LH3qwIq5xpSAnsWpSo-pCgr5zQ9Rlw_6fo78-A4H_wTtA.o72xj55DclBp_H4i3pzFKAH06yOd8M5yLUHTO0IXrrE&dib_tag=se&pd_rd_r=8635ba35-03eb-4884-ae60-d61a94825127&pd_rd_w=R921o&pd_rd_wg=Fcshv&qid=1744561214&refinements=p_85%3A10440599031&rps=1&s=kitchen&sr=1-1-spons&sp_csd=d2lkZ2V0TmFtZT1zcF9hdGZfYnJvd3Nl&th=1'}
        )
        self.assertEqual(response2.get_json()['short_url'], data['short_url'])

        # Test missing URL
        response = self.app.post('/api/shorten', json={})
        self.assertEqual(response.status_code, 400)

        # Test invalid content type
        response = self.app.post('/api/shorten', data="not json")
        self.assertEqual(response.status_code, 400)

    def test_redirect(self):
        # First shorten a URL
        shorten_resp = self.app.post(
            '/api/shorten',
            json={'url': 'https://www.amazon.in/s/ref=mega_sv_s23_5_4_1_1?rh=i%3Akitchen%2Cn%3A1380460031&ie=UTF8&bbn=1380447031'}
        )
        short_code = shorten_resp.get_json()['short_url'].split('/')[-1]

        # Test valid redirect
        response = self.app.get(f'/api/redirect/{short_code}')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, 'https://www.amazon.in/s/ref=mega_sv_s23_5_4_1_1?rh=i%3Akitchen%2Cn%3A1380460031&ie=UTF8&bbn=1380447031')

        # Test invalid short code
        response = self.app.get('/api/redirect/invalid_code')
        self.assertEqual(response.status_code, 404)

    def test_metrics(self):
        # Shorten some URLs first
        domains = [
            'https://example.com',
            'https://example.com/path',
            'https://google.com',
            'https://github.com',
            'https://github.com/project'
        ]
        for url in domains:
            self.app.post('/api/shorten', json={'url': url})

        # Test metrics
        response = self.app.get('/api/metrics')
        self.assertEqual(response.status_code, 200)
        metrics = response.get_json()['top_domains']

        # Should be example.com:2, github.com:2, google.com:1
        self.assertEqual(metrics['example.com'], 2)
        self.assertEqual(metrics['github.com'], 2)
        self.assertEqual(metrics['google.com'], 1)

    def test_redirect_with_headers(self):
        # Test redirect returns proper headers
        shorten_resp = self.app.post(
            '/api/shorten',
            json={'url': 'https://example.org'}
        )
        short_code = shorten_resp.get_json()['short_url'].split('/')[-1]

        response = self.app.get(
            f'/api/redirect/{short_code}',
            headers={'Accept': 'application/json'}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers['Location'], 'https://example.org')
        self.assertEqual(response.get_json()['action'], 'redirect')


if __name__ == '__main__':
    unittest.main()