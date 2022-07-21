import psycopg2

from flask import Flask, render_template
from flask import request

app = Flask(__name__)
@app.route('/')
def home():
	return render_template('home.html')

@app.route('/home', methods = ['GET'])
def homeButton():
	return render_template('home.html')
#Returns the home html with all of the forms
@app.route('/Query1', methods = ['POST'])
def Query1():
	try:
		categoryID = request.form[('categoryID')]
		categoryName = request.form[('categoryName')]
		categoryType = request.form[('categoryType')]
		#This is the data that's given from the first query's form
		pwFile = open("pw.txt", "r")
		pw = pwFile.read()
		pwFile.close()
		connStr = "host='cmpstudb-01.cmp.uea.ac.uk' \
			   dbname= 'dvd18scu' user='dvd18scu' password = " + pw
		conn = psycopg2.connect(connStr)
		#connects to database
		cur = conn.cursor()
		cur.execute('SET search_path to public')
		#sets the path
		cur.execute('INSERT INTO Category (CategoryID, Name, CategoryType) VALUES (%s,%s,%s)',[categoryID, categoryName, categoryType])
		#Executes query 1, inserting the data from the form into the table
		conn.commit()
		#commits changes
		return render_template('home.html', successMessage = 'Category Added successfully.')
		#If its gotten to here it has been successful, so return the page and the
		#success message
	except Exception as e:
		return render_template('home.html', failMessage = 'Operation Failed.', error=e)
		#If it fails, go to the homepage, while returning a failure message, as well
		#as the exception
	finally:
		if conn:
			conn.close()
		#Always close the connection and the end
@app.route('/Query2', methods = ['POST'])
def Query2():
	try:
		categoryID = request.form[('categoryID')]
		#Data from the second query's form
		pwFile = open("pw.txt", "r")
		pw = pwFile.read()
		pwFile.close()
		connStr = "host='cmpstudb-01.cmp.uea.ac.uk' \
			   dbname= 'dvd18scu' user='dvd18scu' password = " + pw
		conn = psycopg2.connect(connStr)
		#Connects to database
		cur = conn.cursor()
		cur.execute('SET search_path to public')
		#sets search path
		cur.execute('DELETE FROM Category WHERE CategoryID =(%s)',[categoryID])
		#Executes the second query, deleting data where the categoryid matches what's
		#given in the form
		conn.commit()
		#commits changes
		return render_template('home.html', successMessage = 'Category deleted successfully or never existed.')
		#If its gotten to here it has been successful, so return the page and the
		#success message
	except Exception as e:
		return render_template('home.html', failMessage = 'Operation Failed.', error=e)
	#If it fails, go to the homepage, while returning a failure message, as well
	#as the exception
	finally:
		if conn:
			conn.close()
		#Always close the connection and the end
@app.route('/Query3', methods = ['GET'])
def Query3():
	try:
		pwFile = open("pw.txt", "r")
		pw = pwFile.read()
		pwFile.close()
		connStr = "host='cmpstudb-01.cmp.uea.ac.uk' \
			   dbname= 'dvd18scu' user='dvd18scu' password = " + pw
		conn = psycopg2.connect(connStr)
		#connects to database
		cur = conn.cursor()
		cur.execute('SET search_path to public')
		#sets search path
		cur.execute('''
			CREATE OR REPLACE VIEW CategorySummary
			AS SELECT
				Category.Name AS Name,
				COUNT(Book.CategoryID) AS Occurences,
				ROUND(AVG(Price),2) AS AveragePrice
			FROM
				Category
			LEFT JOIN Book ON 
				Book.CategoryID = Category.CategoryID
			GROUP BY
				Category.CategoryID;
			''')
		#creates or replaces view
		cur.execute('SELECT * FROM CategorySummary')
		#selects the view
		rows = cur.fetchall()
		#rows equals the view that's been returned
		cur.execute('''
			SELECT
				ROUND(SUM(AveragePrice),2)
			FROM
				CategorySummary
			''')
		#selects the rest of the query from the created view
		total = cur.fetchall()
		#total equals the results from the second part
		return render_template('query3.html', rows=rows, total=total)
		#If it's gotten here it's succeeded, return the page as well as both rows and
		#total to be displayed.
	except Exception as e:
		return render_template('home.html', failMessage = 'Operation Failed.', error=e)
	#If it fails go home and along with a failure message
	finally:
		if conn:
			conn.close()
			#always close the connection at the end
@app.route('/Query4', methods = ['POST'])
def Query4():
	try:
		publisherName = request.form[('publisherName')]
		#Data from form 4 for query 4
		pwFile = open("pw.txt", "r")
		pw = pwFile.read()
		pwFile.close()
		connStr = "host='cmpstudb-01.cmp.uea.ac.uk' \
			   dbname= 'dvd18scu' user='dvd18scu' password = " + pw
		conn = psycopg2.connect(connStr)
		#connect to database
		cur = conn.cursor()
		cur.execute('SET search_path to public')
		#sets search path
		cur.execute('''
			SELECT
				OrderLine.bookid AS "BookID",
				title AS "Book Title",
				count(OrderLine.bookid) AS "Total Orders",
				sum(quantity) AS "Total quantity",
				sum(price*quantity) AS "Total Price",
				sum(unitsellingprice*quantity) AS "Total Unit Selling Price",
				to_char(OrderDate, 'mm') AS "Month",
				to_char(OrderDate, 'yyyy') AS "Year"
			FROM
				Publisher
				JOIN Book ON Book.PublisherID = Publisher.PublisherID
				JOIN OrderLine ON OrderLine.BookID = Book.bookID
				Join ShopOrder ON ShopOrder.ShopOrderID = OrderLine.ShopOrderID

			WHERE
				LOWER(Publisher.name) = LOWER((%s))
			GROUP BY
				"Month",
				"Year",
				title,
				OrderLine.bookid
			ORDER BY
				"Year" DESC,
				"Month"
			''',[publisherName])
		#executes query
		rows = cur.fetchall()
		#rows equals whats returned fro the query
		if rows == []:
			raise Exception('No results')
		#throws exception if no results is found
		return render_template('query4.html', rows=rows)
	#if successful return the query page as well as rows for displaying
	except Exception as e:
		return render_template('home.html', failMessage = 'Operation Failed.', error = e)
	#if failed, go home and display a failure message as well as the error that
	#caused it
	finally:
		if conn:
			conn.close()
			#always close the connection at the end
@app.route('/Query5', methods = ['POST'])
def Query5():
	try:
		bookID = request.form[('bookID')]
		#data from form for query 5
		pwFile = open("pw.txt", "r")
		pw = pwFile.read()
		pwFile.close()
		connStr = "host='cmpstudb-01.cmp.uea.ac.uk' \
			   dbname= 'dvd18scu' user='dvd18scu' password = " + pw
		conn = psycopg2.connect(connStr)
		#connect to database
		cur = conn.cursor()
		cur.execute('SET search_path to public')
		#set search path
		cur.execute('''
			CREATE OR REPLACE VIEW bookHistory
			AS SELECT
				OrderDate AS OrderDate,
				Title AS BookTitle,
				Price AS Price,
				UnitSellingPrice AS UnitSellingPrice,
				SUM(Quantity) AS TotalQuantity,
				Quantity*UnitSellingPrice AS TotalSellingValue,
				Shop.Name AS ShopName
			FROM
				Shop
			JOIN ShopOrder ON ShopOrder.ShopID=Shop.ShopID
			JOIN OrderLine ON OrderLine.ShopOrderID=ShopOrder.ShopOrderID
			JOIN Book ON Book.BookID=OrderLine.BookID
			JOIN Publisher ON Publisher.PublisherID=Book.PublisherID
			WHERE
				Book.BookID = (%s)
			GROUP BY
				ShopOrder.OrderDate,
				Book.Title,
				Book.Price,
				OrderLine.UnitSellingPrice,
				OrderLine.Quantity,
				Shop.Name
			ORDER BY
				OrderDate
			''',[bookID])
		#Inserts the forms data into the query and executes it, creating or replacing
		#a view
		cur.execute('SELECT * FROM bookHistory')
		#selects the view
		bookHistory = cur.fetchall()
		#bookhistory is whats returned
		if bookHistory == []:
			raise Exception('No results')
		#throws exception if no results is found
		cur.execute('''
			SELECT
				SUM(TotalQuantity) AS CompleteTotalQuantity,
				SUM(TotalSellingValue) AS CompleteTotalValue
			FROM
				bookHistory
		''')
		#does second query using data from view

		bookHistoryTotal = cur.fetchall()
		#bookhistorytotal equals whats returned

		return render_template('query5.html', bookHistory=bookHistory, bookHistoryTotal=bookHistoryTotal)
	#if successful return the query's page as well as bookhistory and
	#bookhistorytotal to be displayed
	except Exception as e:
		return render_template('home.html', failMessage = 'Operation Failed.', error=e)
	#if failed return the home page as well as a fail message and the exception
	#that caused it
	finally:
		if conn:
			conn.close()
			#always close the connection at the end
@app.route('/Query6', methods = ['POST'])
def Query6():
	try:
		start = request.form[('dateStart')]
		end = request.form[('dateEnd')]
		#data from form
		pwFile = open("pw.txt", "r")
		pw = pwFile.read()
		pwFile.close()
		connStr = "host='cmpstudb-01.cmp.uea.ac.uk' \
			   dbname= 'dvd18scu' user='dvd18scu' password = " + pw
		conn = psycopg2.connect(connStr)
		#connects to database
		cur = conn.cursor()
		cur.execute('SET search_path to public')
		#sets search path
		cur.execute('''
			SELECT
				table2.salesrepID,
				table2.salesrep,
			COALESCE(table1.totalquantity,0) AS TotalQuantity,
			COALESCE(table1.totalordervalue,0) AS TotalOrderValue
			FROM
				(SELECT
					SalesRep.SalesRepID,
					COALESCE(SUM(OrderLine.Quantity),0) AS TotalQuantity,
					COALESCE(SUM(OrderLine.UnitSellingPrice*OrderLine.Quantity),0) AS TotalOrderValue
				FROM
					SalesRep
						JOIN
							ShopOrder
						ON
							ShopOrder.SalesRepID=SalesRep.SalesRepID
						JOIN
							OrderLine
						ON
							OrderLine.ShopOrderID=ShopOrder.ShopOrderID
				WHERE
					ShopOrder.OrderDate BETWEEN (%s) AND (%s)
				GROUP BY
					SalesRep.SalesRepID
				ORDER BY
					COALESCE(SUM(OrderLine.UnitSellingPrice),0) DESC)
					table1
				RIGHT JOIN
				(SELECT
					SalesRepID,
					name AS SalesRep
				FROM
					SalesRep)
					table2
					ON table1.salesrepid=table2.salesrepid
			GROUP BY
				table2.salesrepid,
				table2.salesrep,
				table1.totalquantity,
				table1.totalordervalue
			ORDER BY
				COALESCE(sum(table1.totalOrderValue),0)DESC;
		''',[start, end])
		#inserts data from form and executes statement
		rep = cur.fetchall()
		#rep equals whats returned from the query

		return render_template('query6.html', rep=rep)
		#return the query's page as well as rep to be displayed

	except Exception as e:
		return render_template('home.html', failMessage = 'Operation Failed.', error=e)
	#if failed return homepage as well as failure message and error that caused
	#it.
	finally:
		if conn:
			conn.close()
			#always close the connection at the end
@app.route('/Query7', methods = ['POST'])
def Query7():
	try:
		categoryID = request.form[('categoryID')]
		percent = request.form[('percent')]
		#data from form for query
		pwFile = open("pw.txt", "r")
		pw = pwFile.read()
		pwFile.close()
		connStr = "host='cmpstudb-01.cmp.uea.ac.uk' \
			   dbname= 'dvd18scu' user='dvd18scu' password = " + pw
		conn = psycopg2.connect(connStr)
		cur = conn.cursor()
		cur.execute('SET search_path to public')
		cur.execute('''
			UPDATE
				book
			SET
				Price = (Price-(Price*(%s))/100)
			WHERE
				CategoryID = (%s);
		''',[percent, categoryID])
		#executes query with data inserted from form
		conn.commit()
		#commits the query's changes

		return render_template('home.html', successMessage = 'Operation successful.')
	#returns homepage along with success message if successful
	except Exception as e:
		return render_template('home.html', failMessage = 'Operation Failed.', error=e)
	#returns homepage and failure message along with the error that caused it
	finally:
		if conn:
			conn.close()
			#always close the connection at the end
if __name__ == '__main__':
		app.run(debug=True)