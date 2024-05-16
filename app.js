document.getElementById('run-query').addEventListener('click', async () => {
    const SQL = await initSqlJs({ locateFile: file => `https://cdnjs.cloudflare.com/ajax/libs/sql.js/1.6.2/${file}` });

    // Yeni bir veritabanı oluştur
    const db = new SQL.Database();

    // Basit bir tablo oluştur ve veri ekle
    db.run("CREATE TABLE test (col1, col2);");
    db.run("INSERT INTO test VALUES (?, ?), (?, ?)", [1, 'foo', 2, 'bar']);

    // Veriyi sorgula
    const res = db.exec("SELECT * FROM test");
    document.getElementById('output').textContent = JSON.stringify(res, null, 2);

    // Veritabanını kapat
    db.close();
});
