from supabase import Client, create_client
# from config import api, url
api_url: str = "https://oqskvdndvhyovlsfzhhm.supabase.co"
key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9xc2t2ZG5kdmh5b3Zsc2Z6aGhtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTUxNTc2MjMsImV4cCI6MjAzMDczMzYyM30.EozoL2WPBSVetxZaRq8yYv3-3Hqb-fpWJXNH1fmnxb4"

def create_supabase_client():
    supabase: Client = create_client(api_url, key)
    return supabase
