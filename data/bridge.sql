INSERT INTO function (id, name, content, type) VALUES ('nexus_memory_bridge', 'Nexus Memory Bridge', 'http://192.168.1.186:8900', 'action') ON CONFLICT (id) DO UPDATE SET content = EXCLUDED.content;
