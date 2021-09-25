from markdowngenerator import MarkdownGenerator
from typing import List
import os
import pyodbc
import sys


def main(argv: List[str]) -> None:
    # Find database
    db_file = "database.accdb"
    if len(argv) > 1:
        db_file = argv[1]

    # Connect to the database file
    try:
        conn = pyodbc.connect(
            r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};" +
            f"Dbq={os.path.join(os.getcwd(), db_file)}"
        )
        cursor = conn.cursor()
        print(f"Connected {db_file}")

    except pyodbc.Error as e:
        sys.exit(f"Error in Connection {e}")

    # Now that you're connected to the database, let's make a spec based on a component
    # for rows in cursor.execute("SELECT "):
    cursor.execute("SELECT * FROM Component")
    for row in cursor.fetchall():
        filename = os.path.join("md-specs", f"{row.Name} Specification.md")
        print(filename)
        with MarkdownGenerator(
            filename=filename,
            enable_TOC=False,
            enable_write=False,
        ) as doc:
            doc.addHeader(1, f"Specification for {row.Name}")
            generate_requirements_for_component(cursor, doc, row[0])
    print("Finished")
    return


def generate_spec(
        cursor: pyodbc.Cursor, 
        doc: MarkdownGenerator, 
        conn: pyodbc.Connection
    ) -> None:
    cursor.execute("SELECT MAX(Number1) FROM Component")
    max_n1 = cursor.fetchone()[0]
    for i in range(1, max_n1 + 1):
        cursor.execute(f"SELECT ID, Name, Description, Number FROM Component WHERE Number1 = {i} AND Number2 IS NULL")
        row = cursor.fetchone()
        doc.addHeader(1, row.Name)
        doc.writeTextLine(row.Description)
        generate_requirements_for_component(cursor, doc, row.ID, conn, 2)
        cursor.execute(f"SELECT MAX(Number2) FROM Component WHERE Number1 = {i}")
        max_n2 = cursor.fetchone()[0]
        if max_n2 is None:
            max_n2 = 1
        for j in range(1, max_n2 + 1):
            cursor.execute(f"SELECT ID, Name, Description, Number FROM Component WHERE Number1 = {i} AND Number2 = {j}")
            row = cursor.fetchone()
            if (row == None):
                break
            doc.addHeader(2, row.Name)
            doc.writeTextLine(row.Description)
            generate_requirements_for_component(cursor, doc, row.ID, conn, 3)
    return


def generate_requirements_for_component_grr(
        component_cursor: pyodbc.Cursor, 
        doc: MarkdownGenerator, 
        componentID: int,
        conn: pyodbc.Connection, 
        header_level: int
    ) -> None:
    req_cursor = conn.cursor()
    component_cursor.execute(f"SELECT * FROM LinkSystemRequirementComponent WHERE ChildID = {componentID}")
    for link_row in component_cursor.fetchall():
        req_cursor.execute(f"SELECT * FROM SystemRequirement WHERE ID = {link_row.ParentID}")
        req_row = req_cursor.fetchone()
        doc.addHeader(header_level, req_row.Number + " " + req_row.Name)
        table = [{
            "Description": req_row.Description,
            "Priority": req_row.cmbPriority,
            "Verification Status": req_row.cmbVerificationStatus
        }]
    return


def generate_requirements_for_component(
        cursor: pyodbc.Connection,
        doc: MarkdownGenerator,
        component: str
    ) -> None:
    cursor.execute(
        f"SELECT ParentID FROM LinkSystemRequirementComponent WHERE ChildID = {component}"
    )
    for entry in cursor.fetchall():
        req_num = entry[0]
        cursor.execute(f"SELECT * FROM SystemRequirement WHERE ID = {req_num}")
        for thing in cursor.fetchall():
            doc.addHeader(2, thing.Number + " " + thing.Name)
            table = [{
                "Description": thing.Description.replace("\r", " ").replace("\n", " "),
                "Priority": thing.cmbPriority,
                "Verification Status": thing.cmbVerificationStatus
            }]
            doc.addTable(dictionary_list=table)
    return


def generate_requirements_for_system_cat(
        cursor: pyodbc.Cursor,
        doc: MarkdownGenerator,
        conn: pyodbc.Connection,
        cat: int
    ) -> None:
    # doc.addHeader(1, "Whole Car Specification")
    # doc.writeTextLine("This document outlines all the requirements for Sunswift 7")
    # cursor.execute("SELECT MAX(Number1) FROM SystemRequirement")
    # max_n1 = cursor.fetchone()[0]
    cursor.execute(f"SELECT * FROM SystemRequirement WHERE Number1 = {cat} AND Number2 IS NULL")
    row = cursor.fetchone()
    doc.addHeader(1, row.Name)
    doc.writeTextLine(row.Description)
    cursor.execute(f"SELECT * FROM SystemRequirement WHERE Number1 = {cat} AND Number2 IS NOT NULL")
    for req_row in cursor.fetchall():
        doc.addHeader(2, req_row.Number + " " + req_row.Name)
        table = [{
            "Description": req_row.Description.replace("\r", " ").replace("\n", " "),
            "Priority": req_row.cmbPriority,
            "Verification Status": req_row.cmbVerificationStatus
        }]
        doc.addTable(dictionary_list=table)
    return


def generate_requirements(cursor, doc, conn):
    """
    This function generates the specification of the whole car based on the requirements themselves.

    Args:
        cursor (cursor): cursor for the database connection
        doc (document): the markdown document
        conn (conn): connection to the database itself
    """
    doc.addHeader(1, "Whole Car Specification")
    doc.writeTextLine("This document outlines all the requirements for Sunswift 7")
    cursor.execute("SELECT MAX(Number1) FROM SystemRequirement")
    max_n1 = cursor.fetchone()[0]
    for i in range(1, max_n1 + 1):
        cursor.execute(f"SELECT * FROM SystemRequirement WHERE Number1 = {i} AND Number2 IS NULL")
        row = cursor.fetchone()
        doc.addHeader(2, row.Name)
        doc.writeTextLine(row.Description)
        cursor.execute(f"SELECT * FROM SystemRequirement WHERE Number1 = {i} AND Number2 IS NOT NULL")
        for req_row in cursor.fetchall():
            doc.addHeader(3, req_row.Number + " " + req_row.Name)
            table = [{
                "Description": req_row.Description.replace("\r", " ").replace("\n", " "),
                "Priority": req_row.cmbPriority,
                "Verification Status": req_row.cmbVerificationStatus
            }]
            doc.addTable(dictionary_list=table)
    return


if __name__ == "__main__":
    main(sys.argv)
